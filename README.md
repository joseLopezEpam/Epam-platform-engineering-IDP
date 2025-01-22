# Epam Platform Engineering IDP

## Overview
This project implements a cloud-based API Gateway capable of receiving and processing payloads containing information about developers, their teams, project names, and the services required for their projects. The system routes these requests to appropriate queues, which trigger the creation of the requested cloud resources. The system also includes dependency handling and retry logic for reliability.

## Key Features
- **API Gateway**: Handles incoming payloads and routes them to appropriate SQS queues.
- **AWS SQS Queues**: Separate queues for different services, including VPC creation, container clusters, and database instances.
- **AWS Lambda Functions**: Processes payloads and sends them to queues.
- **Infrastructure as Code (IaC)**: Automated infrastructure setup using Pulumi.
- **Retry Logic**: Ensures reliable processing of messages.

## Project Structure
```
Epam platform engineering IDP
├── .git              # Git repository metadata
├── .gitignore        # Git ignore file
├── automation        # Contains automation scripts and configurations
├── infra             # Infrastructure as code for the project
├── lambdas           # AWS Lambda function implementations
```

## Requirements
- Python 3.9 or higher
- AWS CLI configured with appropriate permissions
- Pulumi installed

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Epam platform engineering IDP
   ```

2. **Set up a Python virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```



## Usage
1. **Send a sample payload:**
   Use `curl` or a user interface to send the following payload:
   ```json
   {
     "Records": [
       {
         "messageId": "705efacd-3997-4931-b8cf-cd85ca013412",
         "body": "{\"ProjectName\": \"back-service\", \"Services\": [\"vpc\", \"database_instance\"]}",
         "awsRegion": "us-east-1"
       }
     ]
   }
   ```

2. **Monitor the queues:**
   Check the messages in the SQS queues to confirm they have been routed correctly.

3. **Debugging:**
   Logs can be found in the AWS Lambda CloudWatch Logs for debugging issues.

## Key Components

### AWS SQS Queues
- Separate queues for each service (e.g., VPC, container cluster, database instance).
- Dead-letter queues for handling failed messages.

### AWS Lambda Functions
- `processPayloadLambda`: Processes payloads and sends them to the appropriate queues.

### Infrastructure
- Managed using Pulumi for seamless IaC implementation.

## Contribution
Contributions are welcome! Please fork the repository and create a pull request with your changes.


## Contact
For questions or support, please contact the project maintainer at jose_lopez2@epam.com.

