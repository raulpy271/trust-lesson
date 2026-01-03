# :blue_book: Trust Lesson's back-end

<p align="center">
    <a href="https://github.com/raulpy271/trust-lesson/actions/workflows/tests.yml">
        <img src="https://github.com/raulpy271/trust-lesson/actions/workflows/tests.yml/badge.svg">
    </a>
    <a href="https://python-poetry.org/" target="_blank">
        <img src="https://img.shields.io/badge/packaging-poetry-cyan.svg">
    </a>
    <a href="https://github.com/psf/black" target="_blank">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg">
    </a>
    <a href="https://github.com/raulpy271/trust-lesson/" target="_blank">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-brightgreen" alt="Supported Python versions">
    </a>
</p>

Trust Lesson is a virtual learning environment, it's suitable to teach online courses which the lessons need to be synchronous and require to validate the presence of the tutee. 

> Recently, I had lessons to get my driver's license. The lessons were remotely through a meeting service. This service usually takes pictures of the students and later does a manual verification to check that the picture really shows a student watching the classes.
>
> So I had an idea 💡 : **It'd be awesome to create a similar system where human validation is done using computer vision, and I did.**

The project was developed considering scenarios when it's needed to prove that a certain student had watched the lessons, this proof is done by capturing pictures of the students and later validating the images using AI. An example of when this service can be used is when a company need to give a course to professionals who will work in a critical system, then it's needed to had legal garantee that the professionals participated fully of the course.

## :building_construction: Back-end Stack and Infrastructure

![Infrastructure](./assets/trust-lesson-infra.png)

One of the goals when creating this project was to use the best tools, especially ones that I want to improve my knowledge of. The main tools used are:

 - The web framework FastAPI to develop the API back-end.
 - PostgreSQL and Redis to store persistent and volatile data, respectively.
 - The ORM framework SQLAlchemy and the Alembic migration system.
 - Terraform to automate the infrastructure provisioning.
 - Azure Cloud to host the application and to provide some cloud services, like Azure App Services, Computer Vision models and Azure Functions.

Besides, the following tools are used in the development process:

 - Docker to build local images.
 - Poetry to install dependencies and build Python packages.
 - The Black and Flake8 package to enforce code style and check syntax errors.
 - Pytest to automatically run unit tests.
 - Azurite to simulates the Azure Storage locally.
 - Azure Functions Core Tools to run the functions locally.
 - Postman to manually test the API.

## :gear: API Setup

An easy way to start working in the API is to set up a virtual environment and run the unit tests. The [Poetry](https://python-poetry.org/) package manager is used to install the dependencies and create a virtual environment.

With Poetry installed, the following commands install all dependencies, including the development dependencies:

```
# The command must be executed inside the api directory
poetry install with --dev
```

Now, it's possible to enter in the environment with all dependencies included:

```
`poetry env activate`
```

The above command opens a shell inside a virtual environment, which includes the pytest library, the following commands run the unit tests:

```
# Run fastest tests
pytest -m "not slow"

# Run all tests
pytest
```

To make the test execution fast and run only the application code, the test runner uses a lightweight database(In memory SQLite), a fake Redis Client, and even doesn't start a web server.

### Application setup with Docker Compose

To run the application locally using a complete environment is used Docker Compose to create a collection of containers needed to create this environment.

The containers created by docker are:

 - PostgreSQL database.
 - Redis server.
 - FastAPI server.
 - Azurite, this container will simulate the Azure Storage service.
 - Azure Functions Core Tools, will run the functions as if it were the Azure Cloud.

The below commands will build and run the containers in the local machine, they should be run in the root of the project but before that, verify that your system has Docker installed and running.

```
# It will download the public images and build the project from the Dockerfile's.
docker compose build

# Run in background the containers
docker compose up -d
```

After the last command, the environment will be created, run `docker ps` to see which containers are running, execute `docker compose logs` to see the containers logs, and access `localhost:8000/docs/` to see the API routes and how to make requests to them.

To stop the containers run:

```
docker compose down
```

> Note to Postman users: You can use the Postman Collection [Trust_Lesson_API.postman_collection.json](./Trust_Lesson_API.postman_collection.json) to make requests to the API, import the file in Postman to be able to use the collection.

## :rocket: Back-end Deployment

The application is hosted on Microsoft Azure's cloud. The infrastructure needed to host the application is created using Terraform, which makes it possible to create and destroy resources easily and avoid human effort.

The Terraform files located on the root of the project are used to create the resources locally on docker, the Terraform files located in the directory [./infra](./infra) are used to deploy the application to Azure, so the Terraform commands must be executed inside this folder.

To use Terraform with Azure you need to authenticate in your account using the Azure CLI command `az login`, it will open a browser window, and after authentication succeeds the command will show some information, including your subscription ID. Moreover, to create Azure resources using Azure CLI or Terraform you need to create a Service Principal which is the entity associated with the resources created.

After the Service Principal is created, their credentials need to be set as environment variables to be able to make requests to Azure using Terraform, set the credentials like the below snippet:

```
export ARM_CLIENT_ID="<APPID_VALUE>"
export ARM_CLIENT_SECRET="<PASSWORD_VALUE>"
export ARM_SUBSCRIPTION_ID="<SUBSCRIPTION_ID>"
export ARM_TENANT_ID="<TENANT_VALUE>"
```

Now we can create the desired resources using Terraform, to follow the above steps with more details you can read this Terraform tutorial [Azure get started](https://developer.hashicorp.com/terraform/tutorials/azure-get-started/azure-build). The below commands create the resources:

```
# Run the terraform commands inside the proper folder
cd infra

# It will install the azure provider and others also needed. Execute this command only in the first time
terraform init

# It will show what resources will be created
terraform plan

# It will create the resources after confirming with 'yes' 
terraform apply
```

This last command will probably take longer to execute, as a lot of resources will be created, after we finished, it will show in terminal the address and other properties of the created resources.

Don't forgot to destroy the created resources:

```
terraform destroy
```

## :handshake: Contributing

If you want to contribute to the project you are very welcome, the project is still in development and there is a lot of work to do. The development has been tracked in this [Kanban board](https://github.com/users/raulpy271/projects/2), feel free to pick any task and start developing it.

## :book: References

 - :zap: [FastAPI](https://fastapi.tiangolo.com/)
 - :building_construction: [What is Infrastructure as Code with Terraform?](https://developer.hashicorp.com/terraform/tutorials/azure-get-started/infrastructure-as-code)
 - :package: [Docker Docs](https://docs.docker.com/)
 - :cloud: [Microsoft Azure: Cloud Computing Services](https://azure.microsoft.com/en-us/)
 - :robot: [Azure AI Vision](https://azure.microsoft.com/en-us/products/ai-services/ai-vision)
 - :test_tube: [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
 - :alembic: [Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/)
 - :pick: [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
 - :floppy_disk: [Azurite](https://github.com/Azure/Azurite)
