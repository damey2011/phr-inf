import argparse
import base64
import os
from typing import Tuple

import docker as dk
import boto3
from docker.models.images import Image

CLUSTER = ''
SERVICE = ''

DEPLOY_EXISTING_IMAGE = False
DOCKER_IMG_TAG = 'phrasee-test:latest'

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

docker = dk.from_env()


def get_client(mod_name):
    return boto3.client(
        mod_name, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION
    )


def build_local_docker_image() -> Image:
    img, log = docker.images.build(path='.', tag=DOCKER_IMG_TAG, rm=True)
    return img


def get_ecr_login_token_and_url() -> Tuple[str, str]:
    # this is used by docker in order to deploy there
    client = get_client('ecr')
    token = base64.b64decode(
        client.get_authorization_token()['authorizationData'][0]['authorizationToken']
    ).decode('utf-8').replace('AWS:', '')
    endpoint = client.get_authorization_token()['authorizationData'][0]['proxyEndpoint']
    return token, endpoint


def deploy_image(docker_image: Image) -> None:
    print('Deploying docker image\n')
    ecr_login_token, ecr_url = get_ecr_login_token_and_url()
    print(f'Using Token {ecr_login_token} and URL {ecr_url} to login...\n')
    docker.login(username='AWS', password=ecr_login_token, registry=ecr_url)
    print(f'Login Succeeded..\n')
    remote_repo_name = f'{ecr_url.replace("https://", "")}/{DOCKER_IMG_TAG}'
    print(f'Tagging Image to Remote Repository Name: {remote_repo_name} \n')
    docker_image.tag(remote_repo_name, tag='latest')
    print(f'Pushing Docker image to {remote_repo_name}')
    docker.images.push(remote_repo_name, tag='latest')
    print(f'Pushing Done...')


def update_service_and_cluster() -> None:
    client = get_client('ecs')
    print('Updating Service..')
    data = client.update_service(cluster=CLUSTER, service=SERVICE, forceNewDeployment=True)
    for msg in data['service']['events']:
        print(msg.get('message'))
    print('Complete...')


def perform_credential_checks() -> None:
    if not (AWS_ACCESS_KEY and AWS_SECRET_KEY and AWS_REGION):
        raise ValueError('Please make sure "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY" and "AWS_REGION" are '
                         'provided as environmental variables.')


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Deploy to Amazon Elastic Container Service."
    )
    parser.add_argument(
        "-a", "--access", type=str, help='AWS Access ID, if not provided in the environmental variable'
    )
    parser.add_argument(
        "-s", "--secret", type=str, help='AWS Secret Key, if not provided in the environmental variable'
    )
    parser.add_argument(
        "-r", "--region", type=str, help='AWS Region Name, if not provided in the environmental variable'
    )
    parser.add_argument(
        "-sv", "--service", type=str, help='ECS Service Name', required=True
    )
    parser.add_argument(
        "-i", "--image", type=str, help='Image Tag'
    )
    parser.add_argument(
        "-ui", "--use_existing", type=str, help='Add flag to use existing image and not rebuild a new image.',
        nargs='?', default='0', choices=['0', '1']
    )
    parser.add_argument(
        "-c", "--cluster", type=str, help='ECS Cluster', required=True
    )
    return parser


def collect_parameters(args: argparse.Namespace) -> None:
    global AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, SERVICE, CLUSTER, DOCKER_IMG_TAG, DEPLOY_EXISTING_IMAGE
    if args.access:
        AWS_ACCESS_KEY = args.access
    if args.secret:
        AWS_SECRET_KEY = args.secret
    if args.region:
        AWS_REGION = args.region
    if args.image:
        DOCKER_IMG_TAG = args.image
    if args.use_existing:
        if args.image:
            if args.use_existing not in ['0', '1']:
                raise ValueError('Please provide 1 or 0 as value for use_existing')
            else:
                DEPLOY_EXISTING_IMAGE = bool(int(args.use_existing))
        else:
            raise ValueError('You cannot use existing image if you have not provided the image name. Use '
                             '--image <image name> to provide the image name.')
    SERVICE = args.service
    CLUSTER = args.cluster


if __name__ == '__main__':
    collect_parameters(init_argparse().parse_args())
    perform_credential_checks()
    if DEPLOY_EXISTING_IMAGE:
        print('Using Existing Docker Image .... \n')
        image = docker.images.list(DOCKER_IMG_TAG)[-1]
    else:
        print('Building new docker image... \n')
        image = build_local_docker_image()
    deploy_image(image)
    update_service_and_cluster()
