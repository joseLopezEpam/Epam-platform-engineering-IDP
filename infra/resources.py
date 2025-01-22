# resources.py

import json
import pulumi
import pulumi_aws as aws

# Create the dead-letter queue
vpc_dead_letter_queue = aws.sqs.Queue(
    "vpcDeadLetterQueue",
    message_retention_seconds=1209600,  # Retain messages for 14 days
)

# Function to create a queue with an optional dead-letter policy
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

# List of all queues
sqs_queues = [
    vpc_queue,
    container_cluster_queue,
    dummy_deployment_queue,
    compute_instance_queue,
    database_instance_queue,
    stop_vm_queue,
]

# IAM user ARN with access to queues
iam_user_arn = "arn:aws:iam::160885293398:user/jcarlos.lopez2"

# Function to create an SQS queue policy for an IAM user
def create_queue_policy(pulumi_policy_name, queue, user_arn):
    policy_document = queue.arn.apply(lambda arn: {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": f"AllowIAMUser_{user_arn.split('/')[-1]}",
                "Effect": "Allow",
                "Principal": {
                    "AWS": user_arn
                },
                "Action": [
                    "sqs:SendMessage",
                    "sqs:ReceiveMessage",
                    "sqs:DeleteMessage",
                    "sqs:GetQueueAttributes",
                    "sqs:GetQueueUrl"
                ],
                "Resource": arn
            }
        ]
    })

    return aws.sqs.QueuePolicy(
        pulumi_policy_name,
        queue_url=queue.id,
        policy=policy_document.apply(lambda doc: json.dumps(doc)),
        opts=pulumi.ResourceOptions(depends_on=[queue])
    )

# Create queue policies with unique names
create_queue_policy("vpcQueuePolicy", vpc_queue, iam_user_arn)
create_queue_policy("containerClusterQueuePolicy", container_cluster_queue, iam_user_arn)
create_queue_policy("dummyDeploymentQueuePolicy", dummy_deployment_queue, iam_user_arn)
create_queue_policy("computeInstanceQueuePolicy", compute_instance_queue, iam_user_arn)
create_queue_policy("databaseInstanceQueuePolicy", database_instance_queue, iam_user_arn)
create_queue_policy("stopVmQueuePolicy", stop_vm_queue, iam_user_arn)
