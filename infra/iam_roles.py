# iam_roles.py

import json
import pulumi
import pulumi_aws as aws
from resources import (
    vpc_queue,
    container_cluster_queue,
    dummy_deployment_queue,
    compute_instance_queue,
    database_instance_queue,
    stop_vm_queue,
)

# Create the execution role for Lambda
lambda_role = aws.iam.Role(
    "lambdaRole",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }),
)

# List of queue ARNs for Lambda
queue_arns = [
    vpc_queue.arn,
    container_cluster_queue.arn,
    dummy_deployment_queue.arn,
    compute_instance_queue.arn,
    database_instance_queue.arn,
    stop_vm_queue.arn,
]

# Generate a policy document for Lambda
policy_document = pulumi.Output.all(*queue_arns).apply(lambda arns: json.dumps({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sqs:SendMessage",
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes"
            ],
            "Resource": arns
        }
    ]
}))

# Attach the policy to Lambda
lambda_sqs_policy = aws.iam.RolePolicy(
    "lambdaSqsPolicy",
    role=lambda_role.id,
    policy=policy_document
)

# Attach the CloudWatch Logs policy to Lambda
aws.iam.RolePolicyAttachment(
    "lambdaRoleLogs",
    role=lambda_role.id,
    policy_arn="arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
)

# --- Added for the IAM user ---

# ARN of the IAM user who will have access to the queues
iam_user_arn = "arn:aws:iam::160885293398:user/jcarlos.lopez2"

# Define the SQS queues the user will have access to
queue_arns_for_user = [
    vpc_queue.arn,
    container_cluster_queue.arn,
    dummy_deployment_queue.arn,
    compute_instance_queue.arn,
    database_instance_queue.arn,
    stop_vm_queue.arn,
]

# Create a custom IAM policy for the user
sqs_user_policy = aws.iam.Policy(
    "sqsUserPolicy",
    description="Permissions to access specific SQS queues",
    policy=pulumi.Output.all(*queue_arns_for_user).apply(lambda arns: json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "sqs:SendMessage",
                    "sqs:ReceiveMessage",
                    "sqs:DeleteMessage",
                    "sqs:GetQueueAttributes",
                    "sqs:GetQueueUrl"
                ],
                "Resource": arns
            }
        ]
    })),
)

# Attach the custom policy to the IAM user
sqs_user_policy_attachment = aws.iam.PolicyAttachment(
    "sqsUserPolicyAttachment",
    policy_arn=sqs_user_policy.arn,
    users=["jcarlos.lopez2"],  # User name without the full ARN
)
