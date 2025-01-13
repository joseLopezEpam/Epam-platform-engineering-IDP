import json
import pulumi
import pulumi_aws as aws

# ARN of the shared Lambda role
lambda_role_arn = "arn:aws:iam::160885293398:role/lambdaRole-0091e15"

# Function to create a queue policy
def create_queue_policy(queue_arn):
    return json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": lambda_role_arn},
                "Action": [
                    "sqs:ReceiveMessage",
                    "sqs:DeleteMessage",
                    "sqs:GetQueueAttributes"
                ],
                "Resource": queue_arn
            }
        ]
    })

# Dead Letter Queue for handling errors
vpc_dead_letter_queue = aws.sqs.Queue(
    "vpcDeadLetterQueueUnique",
    message_retention_seconds=1209600  # Retention for 14 days
)

# Policy for Dead Letter Queue
vpc_dead_letter_policy = aws.sqs.QueuePolicy(
    "vpcDeadLetterQueuePolicyUnique",
    queue_url=vpc_dead_letter_queue.id,
    policy=vpc_dead_letter_queue.arn.apply(lambda arn: create_queue_policy(arn))
)

# Define other SQS queues
queues = {
    "vpcQueue": aws.sqs.Queue(
        "vpcQueueUnique",
        visibility_timeout_seconds=60,
        message_retention_seconds=1209600,
        redrive_policy=vpc_dead_letter_queue.arn.apply(
            lambda arn: json.dumps({"deadLetterTargetArn": arn, "maxReceiveCount": 5})
        ),
    ),
    "containerClusterQueue": aws.sqs.Queue(
        "containerClusterQueueUnique",
        visibility_timeout_seconds=60,
        message_retention_seconds=1209600,
    ),
    "dummyDeploymentQueue": aws.sqs.Queue(
        "dummyDeploymentQueueUnique",
        visibility_timeout_seconds=60,
    ),
    "computeInstanceQueue": aws.sqs.Queue(
        "computeInstanceQueueUnique",
        visibility_timeout_seconds=60,
    ),
    "databaseInstanceQueue": aws.sqs.Queue(
        "databaseInstanceQueueUnique",
        visibility_timeout_seconds=60,
    ),
    "stopVmQueue": aws.sqs.Queue(
        "stopVmQueueUnique",
        visibility_timeout_seconds=60,
    ),
}

# Apply policies to each queue
for queue_name, queue in queues.items():
    aws.sqs.QueuePolicy(
        f"{queue_name}PolicyUnique",
        queue_url=queue.id,
        policy=queue.arn.apply(lambda arn: create_queue_policy(arn))
    )

# Export the queue URLs for debugging or reference
for queue_name, queue in queues.items():
    pulumi.export(f"{queue_name}Url", queue.url)

pulumi.export("vpcDeadLetterQueueUrl", vpc_dead_letter_queue.url)
