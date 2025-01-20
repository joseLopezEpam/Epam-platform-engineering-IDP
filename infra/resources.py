# resources.py

import json
import pulumi
import pulumi_aws as aws

# Crear la cola de dead-letter
vpc_dead_letter_queue = aws.sqs.Queue(
    "vpcDeadLetterQueue",
    message_retention_seconds=1209600,  # Retener mensajes por 14 días
)

# Función para crear una cola con una política de dead-letter opcional
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

# Crear las colas SQS
vpc_queue = create_queue("vpcQueue", "VPCCreation", vpc_dead_letter_queue.arn)
container_cluster_queue = create_queue("containerClusterQueue", "ContainerClusterCreation")
dummy_deployment_queue = create_queue("dummyDeploymentQueue", "DummyDeployment")
compute_instance_queue = create_queue("computeInstanceQueue", "ComputeInstanceCreation")
database_instance_queue = create_queue("databaseInstanceQueue", "DatabaseInstanceCreation")
stop_vm_queue = create_queue("stopVmQueue", "StopVMs")

# Lista de todas las colas
sqs_queues = [
    vpc_queue,
    container_cluster_queue,
    dummy_deployment_queue,
    compute_instance_queue,
    database_instance_queue,
    stop_vm_queue,
]

# ARN del usuario de IAM que tendrá acceso a las colas
iam_user_arn = "arn:aws:iam::160885293398:user/jcarlos.lopez2"

# Función para crear una política de cola SQS para un usuario de IAM
def create_queue_policy(pulumi_policy_name, queue, user_arn):
    # Construir el documento de política usando apply para manejar el Output
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

    # Crear la política de la cola SQS con un nombre estático y único
    return aws.sqs.QueuePolicy(
        pulumi_policy_name,  # Nombre estático y único para cada política
        queue_url=queue.id,
        policy=policy_document.apply(lambda doc: json.dumps(doc)),
        opts=pulumi.ResourceOptions(depends_on=[queue])
    )

# Crear políticas de cola para cada SQS con nombres únicos
create_queue_policy("vpcQueuePolicy", vpc_queue, iam_user_arn)
create_queue_policy("containerClusterQueuePolicy", container_cluster_queue, iam_user_arn)
create_queue_policy("dummyDeploymentQueuePolicy", dummy_deployment_queue, iam_user_arn)
create_queue_policy("computeInstanceQueuePolicy", compute_instance_queue, iam_user_arn)
create_queue_policy("databaseInstanceQueuePolicy", database_instance_queue, iam_user_arn)
create_queue_policy("stopVmQueuePolicy", stop_vm_queue, iam_user_arn)
