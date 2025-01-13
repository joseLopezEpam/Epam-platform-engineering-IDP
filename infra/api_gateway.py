import pulumi
import pulumi_aws as aws
from lambda_functions import process_payload_lambda

# Create the API Gateway
process_payload_api = aws.apigateway.RestApi(
    "processPayloadApi",
    description="API Gateway for processing payloads and routing to Lambdas.",
)

# Create the /process resource
process_resource = aws.apigateway.Resource(
    "processResource",
    rest_api=process_payload_api.id,
    parent_id=process_payload_api.root_resource_id,
    path_part="process",
)

# Create the POST method
process_post_method = aws.apigateway.Method(
    "processPostMethod",
    rest_api=process_payload_api.id,
    resource_id=process_resource.id,
    http_method="POST",
    authorization="NONE",  # Adjust authorization if needed
)

# Integration (API Gateway -> Lambda)
process_integration = aws.apigateway.Integration(
    "processIntegration",
    rest_api=process_payload_api.id,
    resource_id=process_resource.id,
    http_method=process_post_method.http_method,
    integration_http_method="POST",
    type="AWS_PROXY",
    uri=pulumi.Output.concat(
        "arn:aws:apigateway:",
        aws.config.region,
        ":lambda:path/2015-03-31/functions/",
        process_payload_lambda.arn,
        "/invocations"
    ),
    opts=pulumi.ResourceOptions(depends_on=[process_post_method]),
)

# Grant API Gateway permission to invoke the Lambda
lambda_permission = aws.lambda_.Permission(
    "apiGatewayLambdaPermission",
    action="lambda:InvokeFunction",
    function=process_payload_lambda.name,
    principal="apigateway.amazonaws.com",
    source_arn=pulumi.Output.concat(process_payload_api.execution_arn, "/*/*"),
)

# Deploy the API
process_api_deployment = aws.apigateway.Deployment(
    "processApiDeployment",
    rest_api=process_payload_api.id,
    opts=pulumi.ResourceOptions(depends_on=[process_integration]),
)

# Create the API stage
process_api_stage = aws.apigateway.Stage(
    "processApiStage",
    rest_api=process_payload_api.id,
    deployment=process_api_deployment.id,
    stage_name="dev",
)

# Export the API endpoint
api_endpoint = pulumi.Output.concat(
    "https://",
    process_payload_api.id,
    ".execute-api.",
    aws.config.region,
    ".amazonaws.com/",
    process_api_stage.stage_name,
    "/process"
)

pulumi.export("apiEndpoint", api_endpoint)
