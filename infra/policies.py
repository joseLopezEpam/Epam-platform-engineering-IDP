import json
import pulumi
import pulumi_aws as aws
from infra.test_sqs_queues import queues
import hashlib

# ARN del único rol Lambda compartido
lambda_role_arn = "arn:aws:iam::160885293398:role/lambdaRole-0091e15"

def apply_policies():
    # Dictionary to track which queues have been processed
    processed_policies = {}

    for queue_name, queue in queues.items():
        # Skip if this queue already has a policy processed
        if queue_name in processed_policies:
            continue

        # Generate a unique name for the policy
        def create_policy(queue_arn):
            unique_policy_name = f"{queue_name}-policy-{pulumi.get_stack()}"

            # Define the policy JSON
            policy_document = json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": lambda_role_arn
                        },
                        "Action": [
                            "sqs:ReceiveMessage",
                            "sqs:DeleteMessage",
                            "sqs:GetQueueAttributes"
                        ],
                        "Resource": queue_arn
                    }
                ]
            })

            # Create the QueuePolicy resource
            processed_policies[queue_name] = aws.sqs.QueuePolicy(
                unique_policy_name,
                queue_url=queue.url,
                policy=policy_document
            )

        # Use apply to handle Output[T]
        queue.arn.apply(create_policy)

# Call the function to apply policies
apply_policies()
