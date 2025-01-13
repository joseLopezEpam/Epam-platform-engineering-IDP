import os
import pulumi
import pulumi.asset as asset
import pulumi_aws as aws
from iam_roles import lambda_role
from resources import (
    vpc_queue, container_cluster_queue, dummy_deployment_queue,
    compute_instance_queue, database_instance_queue, stop_vm_queue
)

LAMBDA_BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "lambdas")

# Helper function to create a Lambda function
def create_lambda(name, lambda_path, handler, environment_vars=None):
    return aws.lambda_.Function(
        name,
        runtime="python3.9",
        code=asset.FileArchive(os.path.join(LAMBDA_BASE_PATH, lambda_path)),
        handler=handler,
        role=lambda_role.arn,
        environment=aws.lambda_.FunctionEnvironmentArgs(variables=environment_vars or {}),
    )

# Define the `process_payload` Lambda
process_payload_lambda = create_lambda(
    "processPayloadLambda",
    "process_payload",
    "src/handler.lambda_handler",
    {
        "VPC_QUEUE_URL": vpc_queue.url,
        "CONTAINER_CLUSTER_QUEUE_URL": container_cluster_queue.url,
        "DUMMY_DEPLOYMENT_QUEUE_URL": dummy_deployment_queue.url,
        "COMPUTE_INSTANCE_QUEUE_URL": compute_instance_queue.url,
        "DATABASE_INSTANCE_QUEUE_URL": database_instance_queue.url,
        "STOP_VM_QUEUE_URL": stop_vm_queue.url,
    }
)
