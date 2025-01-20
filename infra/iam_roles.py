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

# Crear el rol de ejecución para Lambda
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

# Lista de ARNs de las colas para Lambda
queue_arns = [
    vpc_queue.arn,
    container_cluster_queue.arn,
    dummy_deployment_queue.arn,
    compute_instance_queue.arn,
    database_instance_queue.arn,
    stop_vm_queue.arn,
]

# Generar un documento de política para Lambda
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

# Adjuntar la política a Lambda
lambda_sqs_policy = aws.iam.RolePolicy(
    "lambdaSqsPolicy",
    role=lambda_role.id,
    policy=policy_document
)

# Adjuntar la política de CloudWatch Logs a Lambda
aws.iam.RolePolicyAttachment(
    "lambdaRoleLogs",
    role=lambda_role.id,
    policy_arn="arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
)

# --- Añadido para el usuario de IAM ---

# ARN del usuario de IAM que tendrá acceso a las colas
iam_user_arn = "arn:aws:iam::160885293398:user/jcarlos.lopez2"

# Definir las colas SQS a las que el usuario tendrá acceso
queue_arns_for_user = [
    vpc_queue.arn,
    container_cluster_queue.arn,
    dummy_deployment_queue.arn,
    compute_instance_queue.arn,
    database_instance_queue.arn,
    stop_vm_queue.arn,
]

# Crear una política de IAM personalizada para el usuario
sqs_user_policy = aws.iam.Policy(
    "sqsUserPolicy",
    description="Permisos para acceder a colas SQS específicas",
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

# Adjuntar la política personalizada al usuario de IAM
sqs_user_policy_attachment = aws.iam.PolicyAttachment(
    "sqsUserPolicyAttachment",
    policy_arn=sqs_user_policy.arn,
    users=["jcarlos.lopez2"],  # Nombre del usuario sin el ARN completo
)
