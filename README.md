# Deploying Python code to AWS Lambda with CDK

Deploying Python code to AWS Lambda using the AWS CDK is confusing especially when there are so many different methods and options available.  I honestly feel right now the true AWS Serverless *Best Practice* is yet to fully emerge so I tend to tread carefully and make the choices that work for my teams and projects.  I also tend to move slowly with adopting the next BIG thing and make sure I play with and understand the choices I am making.  So I have put this project example together for my own use and to use as a basis for Serverless teams that I assist and accelerate in my day to day work life, it has the things that I like and prefer to use and understand.

There are a few considerations when building out a sane project directory structure for a Serverless Service built around AWS Lambda packaged and deployed using the AWS CDK.

**Important Note:** This repo is a work in progress and under constant churn right now as I work to complete a full end to end solution of dev, package, test and deploy.

## Project Structure Considerations

1. Lambda function code must be usable in test suite files.
2. Lambda service functions must be able to use relative code modules and must remain executable in both test suites and by the AWS Lambda runtime.
3. Lambda functions must only include the dependencies they directly use so that lambda function sizes are kept to a minimum to ease cold start time pressure.
4. CDK infrastructure for Lambda service components must be co-located with the lambda function to ease refactoring and ensure related service elements are kept together in a single unit
5. CDK Infrastructure for each service component must be implemented as a CDK Construct and not a stack.  This will enable faster refactoring and enable flexible stack creation and re-use in real cloud testing.
6. CDK Constructs should reference real folders and the "cdk deploy" should be the thing that does all the work of packaging and deploying so there are no hidden steps.
7. Sometimes 6 is not always achievable and I have added some "magic" in the requirements.txt creation which is explained further down in the README around my use of poetry for dependency management.

## Hexagonal Architecture

There has been a lot of talk about [Hexagonal Architectures](https://alistair.cockburn.us/hexagonal-architecture/) in the AWS Serverless wold this year and I have written some articles on this topic which you can find on [my blog](https://blog.walmsles.io).  In this repo I use the Dependency Inversion principle in building out Ports and Adapters to create loosely coupled classes for accesing AWS Cloud resources.  This helps in reducing the need for mocking AWS SDK calls in order to test the Microservice code you are writing which is often hard or problematic for developers new to AWS Serverless.

I am using this repo to also explore this concept and the ideas presented here will change as I mature my understanding through building and testing.

## Where to Start?

I have based this project structure on the AWS Sample repo [aws-cdk-project-structure-python](https://github.com/aws-samples/aws-cdk-project-structure-python) on GitHub which is a great starting point.  It uses the [aws-cdk-aws-lambda-python-alpha](https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_lambda_python_alpha.html) construct for deploying Lambda code.

I have also borrowed some project structure and management ideas directly from [aws-lambda-powertools](https://github.com/awslabs/aws-lambda-powertools-python) for python which is a great example of an Open Source repo for a python project!

**NOTE:** The first time you execute a synth or deploy takes a long time. There is no output letting you know what is going on while the docker images are being downloaded to perform the initial packaging (See [Github Issue](https://github.com/aws/aws-cdk/issues/20390)) - once this is done synth and deploy are much faster, so do hang in there for the first synth/deploy.

I have made the following changes/additions:

- **poetry** used for packaging instead of pip
- All requirements are managed at the root level including runtime dependencies for Lambda functions to be deployed.
- added **Makefile** to simplify the management of the project.
- relocated stack and toolchain files to **cdk** folder to keep the root folder cleaner.
- Added some useful conventions (see below) to enable new developers to understand more clearly where things live when adding to a project.
- changed how lambda runtime **requirements.txt** files work - these are now generated from the central poetry dependencies.

## Useful Conventions

The following conventions are used in this project setup and must be adhered to for all the processes to work correctly.  The conventions are straight-forward and intended to add logical process over the projects.

### Project Folders

#### cdk

This folder is where common cdk modules should exist along with the CDK Stack to be deployed by the service.  The **stack.py** is the file to modify and include all your constructs from the services folder.

#### tests

This folder contains pytest files for testing your service code and is broken down into:

- Unit - stand-alone unit test suites testing individual code modules and functions
- Integration - Tests which create cloud infrastructure based on the construct defined by the service.
- E2E - End to end tests to validate the service is working.

#### services

This folder is where each of your micro-service components is defined.  Each folder should represent a complete component of your solution.  The folder names are important here as they will tie into how Python dependencies are packaged for each micro-service (see Poetry section below).  Service folder structure use the following:

```
├── infrastructure.py
└── runtime
    ├── __init__.py
    ├── adapters
    │   ├── __init__.py
    │   ├── fake_storage.py
    │   ├── file_storage.py
    │   └── ports
    │       ├── __init__.py
    │       ├── event_port.py
    │       └── file_port.py
    ├── api.py
    ├── event.py
    └── requirements.txt
```
- **infrastructure.py** contains the CDK construct code for the service.  This should always be a construct and not a stack since this enables a single stack to be created for a service which I feel is critical.  Thsi also enables a component to be split-out and re-used pretty quickly as you have built for this already.
- **runtime** contains the actual Lambda code for the service (if Lamda is being used) and is the folder that the **PythonFunction** construct packages for you.  teh benefit of using this alpha feature is proper Lambda packaging is done in a Lambda compatible environment according to your chosen Architecture.
- **adapters** is used to house adapter implementation for the Service - we are using Hexagonal Achitecture here and ports and adapters are critical in enabling cloud isolation and simpler testing.
- **adapters/ports** are the interfaces used by the adapter implementations.

### Poetry - Managing Python Dependencies

I like poetry for managing dependencies, in particular I like the **group** option for [adding dependencies](https://python-poetry.org/docs/cli/#add).  A key need is to ensure that each Lambda deployment package is as small as possible.  Using poetry all dependecies for each service can be added to a **group** for each service within the **service** folder, this enables the `make deps` target to look for the **runtime** folders and perform a `poetry export --with=group-name` to create the **requirements.txt** for packaging by the *8PythonLambda** construct.

There is a `make-deps.sh` bash script that is used to generate the requirements.txt files for each runtime folder.

When adding dependencies for a **service** with a runtime folder in the `service/event_api` folder you can use:

```
$ poetry add aws-lambda-powertools --group=event_api
```

The same dependency can be added to multiple groups and this is okay - poetry takes care of this for you.  The advantage is you get a customised **requirements.txt** for each service with only thier dependencies and the tooling in the repo will naturally deal with new services.



# Using Podman in place of Docker

The AWS CDK **PythonFunction** construct requires docker in order to package the lambda.  I am working in an enterprise environment and am not enabled to install the docker desktop (I do not use it enough to qualify for a funding code to license the desktop tool).

Instead I use podman on my mac which can be used as a drop-in replacement to docker.  In order to use `podman` you will need the following installed:

- [Homebrew](https://brew.sh)
- [Podman](https://podman.io)
- `scripts/docker` placed into your local env path

The `docker` script pushes all commands staight through to podman and enables AWS CDK PythonFunction to do a full deployment.
