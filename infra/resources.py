import json
import pulumi
import pulumi_aws as aws

# Create the dead-letter queue
vpc_dead_letter_queue = aws.sqs.Queue(
    "vpcDeadLetterQueue",
    message_retention_seconds=1209600,  # Retain messages for 14 days
)

# Function to create a queue with a dead-letter policy
def create_queue(name, purpose, dead_letter_arn=None):
    redrive_policy = (
        dead_letter_arn.apply(
            lambda arn: json.dumps({"deadLetterTargetArn": arn, "maxReceiveCount": 5})
        )
        if dead_letter_arn
        else None
    )

    return aws.sqs.Queue(
        name,
        visibility_timeout_seconds=60,
        message_retention_seconds=1209600,
        redrive_policy=redrive_policy,
        tags={"Purpose": purpose},
    )

# Create SQS queues
vpc_queue = create_queue("vpcQueue", "VPCCreation", vpc_dead_letter_queue.arn)
container_cluster_queue = create_queue("containerClusterQueue", "ContainerClusterCreation")
dummy_deployment_queue = create_queue("dummyDeploymentQueue", "DummyDeployment")
compute_instance_queue = create_queue("computeInstanceQueue", "ComputeInstanceCreation")
database_instance_queue = create_queue("databaseInstanceQueue", "DatabaseInstanceCreation")
stop_vm_queue = create_queue("stopVmQueue", "StopVMs")
