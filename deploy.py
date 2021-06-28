import os
from pathlib import Path
import sys

from bentoml.utils.ruamel_yaml import YAML
from bentoml.saved_bundle import load_from_dir
from utils import (
    call_sam_command,
    create_ecr_repository_if_not_exists,
    get_ecr_login_info,
    generate_docker_image_tag,
    build_docker_image,
    push_docker_image_to_repository
)


def _create_aws_lambda_cloudformation_template_file(
    project_dir,
    api_names,
    bento_service_name,
    ecr_image_uri,
    memory_size: int,
    timeout: int,
):
    template_file_path = os.path.join(project_dir, "template.yaml")
    yaml = YAML()
    sam_config = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Transform": "AWS::Serverless-2016-10-31",
        "Globals": {
            "Function": {"Timeout": timeout, "MemorySize": memory_size},
            # "Api": {
            # "BinaryMediaTypes": ["image~1*"],
            # "Cors": "'*'",
            # "Auth": {
            # "ApiKeyRequired": False,
            # "DefaultAuthorizer": "NONE",
            # "AddDefaultAuthorizerToCorsPreflight": False,
            # },
            # },
        },
        "Resources": {},
    }
    for api_name in api_names:
        sam_config["Resources"][api_name] = {
            "Type": "AWS::Serverless::Function",
            "Properties": {
                "FunctionName": f"{api_name}",
                "PackageType": "Image",
                "ImageUri": ecr_image_uri,
                "ImageConfig": {"Command": [f"app.{api_name}"]},
                "Events": {
                    "Api": {
                        "Type": "Api",
                        "Properties": {
                            "Path": "/{}".format(api_name),
                            "Method": "post",
                        },
                    }
                },
                "Environment": {
                    "Variables": {
                        "BENTOML_BENTO_SERVICE_NAME": bento_service_name,
                        "BENTOML_API_NAME": api_name,
                    }
                },
            },
        }

    yaml.dump(sam_config, Path(template_file_path))

    # We add Outputs section separately, because the value should not
    # have "'" around !Sub
    with open(template_file_path, "a") as f:
        f.write(
            """\
Outputs:
  EndpointUrl:
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.\
amazonaws.com/Prod"
    Description: URL for endpoint
"""
        )
    return template_file_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Please provide Bundle path")
    bundle_path = sys.argv[1]

    bentobundle = load_from_dir(bundle_path)
    aws_region = "ap-south-1"
    model_repo_name = "irisclassifier"

    # Build and Push docker image
    registry_id, registry_uri = create_ecr_repository_if_not_exists(
        aws_region, model_repo_name
    )
    registry_url, username, password = get_ecr_login_info(aws_region, registry_id)
    image_tag = generate_docker_image_tag(registry_uri, "irisclassifier", "")
    print('Building Image...')
    build_docker_image(
        context_path=bundle_path,
        image_tag=image_tag,
    )
    print('Pushing Image...')
    push_docker_image_to_repository(image_tag, username=username, password=password)

    # Parse the APIs in bundle and build and deploy with SAM
    api_names = [api.name for api in bentobundle.inference_apis]
    template_file_path = _create_aws_lambda_cloudformation_template_file(
        project_dir=bundle_path,
        api_names=api_names,
        bento_service_name=bentobundle.name,
        ecr_image_uri=image_tag,
        memory_size=500,
        timeout=60,
    )
    print("SAM Template file generated at ", template_file_path)
    return_code, stdout, stderr = call_sam_command(
        [
            "deploy",
            "-t",
            template_file_path.split("/")[-1],
            "--stack-name",
            "iris-classifier",
            "--image-repository",
            image_tag,
            "--capabilities",
            "CAPABILITY_IAM",
            "--region",
            aws_region,
            "--no-confirm-changeset",
        ],
        project_dir=bundle_path,
        region=aws_region,
    )
    if return_code != 0:
        print(return_code, stdout, stderr)
    else:
        print("Upload success!")
