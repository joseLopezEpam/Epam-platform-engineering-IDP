import os
import pkg_resources
import pulumi
import pulumi.automation as auto

def create_or_select_stack(stack_name: str, pulumi_program_path: str):
    """
    Creates or selects the stack `stack_name`, with the Pulumi code located in `pulumi_program_path`.
    """
    try:
        # Select existing stack
        stack = auto.select_stack(
            stack_name,
            work_dir=pulumi_program_path
        )
        print(f"Selected existing stack: {stack_name}")
    except auto.StackNotFoundError:
        # Create stack if it doesn't exist
        stack = auto.create_stack(
            stack_name,
            work_dir=pulumi_program_path
        )
        print(f"Created new stack: {stack_name}")

    return stack

def run_deploy():
    stack_name = "dev"
    pulumi_program_path = os.path.join(os.getcwd(), "infra")  # Use absolute path

    # Check the Pulumi runtime version
    pulumi_version = pkg_resources.get_distribution("pulumi").version
    print(f"Pulumi runtime version: {pulumi_version}")

    # Create or select the stack
    stack = create_or_select_stack(stack_name, pulumi_program_path)

    # Optional configuration (AWS region)
    stack.set_config("aws:region", auto.ConfigValue(value="us-east-1"))

    # Execute pulumi up
    up_res = stack.up(on_output=print)

    # Example: print an output from your Pulumi program
    api_endpoint = up_res.outputs.get("apiEndpoint")
    if api_endpoint:
        print(f"API Endpoint => {api_endpoint.value}")


if __name__ == "__main__":
    run_deploy()
