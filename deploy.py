from bentoml.saved_bundle import load_from_dir
import os
from pathlib import Path
from bentoml.utils.ruamel_yaml import YAML


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
    bentobundle = load_from_dir("./model-bundle/")
    api_names = [api.name for api in bentobundle.inference_apis]
    ecr_image_uri = (
        "213386773652.dkr.ecr.ap-south-1.amazonaws.com/irisclassifier:latest"
    )
    print(api_names)

    template_file_path = _create_aws_lambda_cloudformation_template_file(
        project_dir="./model-bundle",
        api_names=api_names,
        bento_service_name=bentobundle.name,
        ecr_image_uri=ecr_image_uri,
        memory_size=500,
        timeout=60,
    )
