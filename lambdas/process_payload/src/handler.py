import json
import os
import boto3

def lambda_handler(event, context):
    """
    Lee el payload de API Gateway, valida, y lo envía a distintas colas 
    según la lista de servicios solicitados.
    """
    try:
        sqs_client = boto3.client("sqs")

        # Log completo del evento recibido
        print("Evento recibido en Lambda:", json.dumps(event, indent=4))

        # Decodificar el cuerpo si proviene de API Gateway
        if "body" in event:
            try:
                event = json.loads(event["body"])
                print("Evento decodificado desde API Gateway:", json.dumps(event, indent=4))
            except json.JSONDecodeError as e:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "El body no es un JSON válido."})
                }

        # Validar que existan registros en 'Records'
        records = event.get("Records", [])
        if not records:
            print("No se encontraron registros en 'Records'. Evento recibido:", json.dumps(event, indent=4))
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "No se encontraron registros en 'Records'."})
            }

        # Iterar sobre los registros y procesar cada uno
        for record in records:
            try:
                # Decodificar el contenido del body (que está como cadena JSON)
                body = json.loads(record["body"])
            except json.JSONDecodeError as e:
                print(f"Error al decodificar 'body': {str(e)}")
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "El 'body' no es un JSON válido."})
                }

            # Extraer los datos del payload
            project_name = body.get("ProjectName")
            services = body.get("Services", [])

            # Validar que existan los campos necesarios
            if not project_name or not services:
                print("Datos incompletos en el payload:", body)
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "Datos incompletos. Se requiere 'ProjectName' y 'Services'."})
                }

            # Mapa de colas
            queue_map = {
                "vpc": os.environ.get("VPC_QUEUE_URL"),
                "container_cluster": os.environ.get("CONTAINER_CLUSTER_QUEUE_URL"),
                "dummy_deployment": os.environ.get("DUMMY_DEPLOYMENT_QUEUE_URL"),
                "compute_instance": os.environ.get("COMPUTE_INSTANCE_QUEUE_URL"),
                "database_instance": os.environ.get("DATABASE_INSTANCE_QUEUE_URL"),
                "stop_vm": os.environ.get("STOP_VM_QUEUE_URL")
            }

            # Procesar servicios y enviar a las colas correspondientes
            for service in services:
                queue_url = queue_map.get(service)
                if queue_url:
                    # En lugar de solo enviar ProjectName y Service,
                    # enviamos 'body' completo:
                    response = sqs_client.send_message(
                        QueueUrl=queue_url,
                        MessageBody=json.dumps(body)
                    )
                    print(f"Enviado a la cola {service}: {body}. MessageId: {response['MessageId']}")
                else:
                    print(f"No se encontró una cola para el servicio: {service}")


        # Respuesta exitosa
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Mensajes enviados correctamente."})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Error interno: {str(e)}"})
        }
