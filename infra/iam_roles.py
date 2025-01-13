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

# Create the Lambda execution role
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

# List of queue ARNs
queue_arns = [
    vpc_queue.arn,
    container_cluster_queue.arn,
    dummy_deployment_queue.arn,
    compute_instance_queue.arn,
    database_instance_queue.arn,
    stop_vm_queue.arn,
]

# Generate a policy document for all the queues
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

# Attach the policy to the Lambda role
lambda_sqs_policy = aws.iam.RolePolicy(
    "lambdaSqsPolicy",
    role=lambda_role.id,
    policy=policy_document
)

# Attach CloudWatch Logs policy
aws.iam.RolePolicyAttachment(
    "lambdaRoleLogs",
    role=lambda_role.id,
    policy_arn="arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
)
