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

- Inside the project root, there is a file named `deploy.py` which is used to build the docker image, deploy it to ECR and 
deploy updates to the services already created (python-api-dev, python-api-qa, python-api-prod), this file can take 7 possible 
arguments namely;
    - `--access/-a`: AWS Access ID, if not provided in the environmental variable as `AWS_ACCESS_KEY_ID`.
    - `--secret/-s`: AWS Secret Key, if not provided in the environmental variable as `AWS_SECRET_ACCESS_KEY`.
    - `--region/-r`: AWS Region Name, if not provided in the environmental variable as `AWS_REGION`.
    - `--image/-i`: The tag name we wish to give every freshly build docker image. This needs to match the name of the 
    repository created for hosting our images in ECR. If our repository name is `phrasee-test`, you would want to pass in 
    `phrasee-test`.   
    - `--use_existing/-ui`: (Optional) Sometimes, we might want to use existing built image rather than 
    building at all times. You can pass in `1` or `0` as this argument which represents True and False respectively. 
    False being the default.  
    - `--cluster/-c`: Provide the ECS cluster name here.
    
    To deploy to `python-api-dev` service. We can run:
    
    ```bash
    python deploy.py -a <AWS_ACCESS_ID> -s <AWS_SECRET> -r eu-west-1 -sv python-api-dev -i phrasee-test -c python-api-cluster 
    ```

- The instance would be accessible through the IP assigned to the new task created under the service specified for deployment 
which varies unless an elastic IP (fixed) is assigned.
