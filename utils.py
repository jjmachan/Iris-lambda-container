import subprocess
import logging
import os
import boto3
import base64

logger = logging.getLogger(__name__)


def call_sam_command(command, project_dir, region):
    command = ["sam"] + command

    # We are passing region as part of the param, due to sam cli is not currently
    # using the region that passed in each command.  Set the region param as
    # AWS_DEFAULT_REGION for the subprocess call
    logger.debug('Setting envar "AWS_DEFAULT_REGION" to %s for subprocess call', region)
    copied_env = os.environ.copy()
    copied_env["AWS_DEFAULT_REGION"] = region

    proc = subprocess.Popen(
        command,
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=copied_env,
    )
    stdout, stderr = proc.communicate()
    logger.debug("SAM cmd %s output: %s", command, stdout.decode("utf-8"))
    return proc.returncode, stdout.decode("utf-8"), stderr.decode("utf-8")


def get_ecr_login_info(region, repository_id):
    ecr_client = boto3.client("ecr", region)
    token = ecr_client.get_authorization_token(registryIds=[repository_id])
    username, password = (
        base64.b64decode(token["authorizationData"][0]["authorizationToken"])
        .decode("utf-8")
        .split(":")
    )
    registry_url = token["authorizationData"][0]["proxyEndpoint"]

    return registry_url, username, password
