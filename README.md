# Simple Sentence Generator
Application is in Python and based on Flask framework. This deployment runs on top of Docker and uses 
the Amazon Elastic Container Service.


## AWS Deployment
Key infrastructures to this include:
- Amazon Elastic Container Registry (ECR) for [managing our docker images](https://docs.aws.amazon.com/cli/latest/reference/ecr/create-repository.html).
- Elastic Container Service (ECS) with Fargate


### Requirements

Before beginning the process, you need to have 
[docker installed](https://docs.docker.com/engine/installation/#installation).


### Assumptions

- This assumes sufficient IAM privileges.
- A repository is created in the ECR to keep the docker image built.
- There are already existing ECS cluster and services to use for this demo.


#### Steps 

- Navigate into the project folder.

- Run the unit tests using:
    ```bash
    nose2
    ```
  Should all go well (No test failures), move on to the next step.

- Inside the project root, there is a script file named `deploy.py` which is used to build the docker image, upload it to ECR and 
deploy updates to the services already created (python-api-dev, python-api-qa or python-api-prod in this case), this file can take 7 possible 
arguments namely;
    - `--access/-a`: (Optional) AWS Access ID, falls back to environmental variable `AWS_ACCESS_KEY_ID`.
    - `--secret/-s`: (Optional) AWS Secret Key, falls back to environmental variable `AWS_SECRET_ACCESS_KEY`.
    - `--region/-r`: (Optional) AWS Region Name, falls back to environmental variable `AWS_REGION`.
    - `--image/-i`: (Optional) The tag name we wish to give the built docker image. This needs to match the name of the 
    repository created for hosting our images in ECR. If our repository name is `phrasee-test`, you would want to pass in 
    `phrasee-test`. Default provided is `phrasee-test`.
    - `--use_existing/-ui`: (Optional) Sometimes, we might want to use existing built image rather than 
    building at all times. You can pass in `1` to use an existing image which has the name you provided in `--image/-a`  or 
    `0` leave out the argument to rebuild a new image.
    - `--cluster/-c`: Provide the ECS cluster name here.
    - `--service/-s`: ECS service name. Here, could be one of the three (python-api-dev, python-api-qa or python-api-prod).
    
    To deploy to `python-api-dev` service. We can run:
    
    ```bash
    python deploy.py -a <AWS_ACCESS_ID> -s <AWS_SECRET> -r eu-west-1 -sv python-api-dev -i phrasee-test -c python-api-cluster 
    ```

- The instance would be accessible through the IP assigned to the new task created under the service specified for deployment 
which varies unless an elastic IP (fixed) is assigned.
