import json
import os
import boto3

def lambda_handler(event, context):
    """
    Reads the API Gateway payload, validates it, and sends it to different queues 
    based on the requested services.
    """
    try:
        sqs_client = boto3.client("sqs")

        # Log the received event
        print("Event received in Lambda:", json.dumps(event, indent=4))

        # Decode the body if it comes from API Gateway
        if "body" in event:
            try:
                event = json.loads(event["body"])
                print("Decoded event from API Gateway:", json.dumps(event, indent=4))
            except json.JSONDecodeError:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "The body is not valid JSON."})
                }

        # Validate the presence of 'Records'
        records = event.get("Records", [])
        if not records:
            print("No records found in 'Records'. Event received:", json.dumps(event, indent=4))
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "No records found in 'Records'."})
            }

        # Process each record
        for record in records:
            try:
                body = json.loads(record["body"])
            except json.JSONDecodeError:
                print("Error decoding 'body'")
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "The 'body' is not valid JSON."})
                }

            # Extract data from the payload
            project_name = body.get("ProjectName")
            services = body.get("Services", [])

            # Validate required fields
            if not project_name or not services:
                print("Incomplete data in the payload:", body)
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "Incomplete data. 'ProjectName' and 'Services' are required."})
                }

            # Queue mapping
            queue_map = {
                "vpc": os.environ.get("VPC_QUEUE_URL"),
                "container_cluster": os.environ.get("CONTAINER_CLUSTER_QUEUE_URL"),
                "dummy_deployment": os.environ.get("DUMMY_DEPLOYMENT_QUEUE_URL"),
                "compute_instance": os.environ.get("COMPUTE_INSTANCE_QUEUE_URL"),
                "database_instance": os.environ.get("DATABASE_INSTANCE_QUEUE_URL"),
                "stop_vm": os.environ.get("STOP_VM_QUEUE_URL")
            }

            # Process services and send to respective queues
            for service in services:
                queue_url = queue_map.get(service)
                if queue_url:
                    response = sqs_client.send_message(
                        QueueUrl=queue_url,
                        MessageBody=json.dumps(body)
                    )
                    print(f"Sent to queue {service}: {body}. MessageId: {response['MessageId']}")
                else:
                    print(f"No queue found for service: {service}")

        # Successful response
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Messages sent successfully."})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": f"Internal error: {str(e)}"})
        }
