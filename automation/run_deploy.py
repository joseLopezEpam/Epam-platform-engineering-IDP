import os
import pkg_resources
import pulumi
import pulumi.automation as auto


def create_or_select_stack(stack_name: str, pulumi_program_path: str):
    """
    Crea o selecciona el stack `stack_name`, indicando que el código Pulumi
    está en la carpeta `pulumi_program_path` (work_dir).
    """
    try:
        # Selecciona stack existente
        stack = auto.select_stack(
            stack_name,
            work_dir=pulumi_program_path
        )
        print(f"Selected existing stack: {stack_name}")
    except auto.StackNotFoundError:
        # Crea stack si no existe
        stack = auto.create_stack(
            stack_name,
            work_dir=pulumi_program_path
        )
        print(f"Created new stack: {stack_name}")

    return stack


def run_deploy():
    # Nombre del stack que quieres usar
    stack_name = "dev"

    # Ruta a la carpeta donde se encuentra "Pulumi.yaml"
    # (por ejemplo, si "automation/" está al mismo nivel que "infra/",
    #  usar "../infra" u otra ruta relativa)
    pulumi_program_path = os.path.join("..", "infra")

    # Comprobamos versión de Pulumi instalada en runtime
    pulumi_version = pkg_resources.get_distribution("pulumi").version
    print(f"Pulumi runtime version: {pulumi_version}")

    # Creamos o seleccionamos stack
    stack = create_or_select_stack(stack_name, pulumi_program_path)

    # Config opcional (la región AWS que usarás)
    stack.set_config("aws:region", auto.ConfigValue(value="us-east-1"))

    # Ejecutamos pulumi up
    up_res = stack.up(on_output=print)

    # Ejemplo: imprimir un output de tu programa Pulumi
    # (supongamos definiste un output "apiEndpoint" en infra/main.py)
    api_endpoint = up_res.outputs.get("apiEndpoint")
    if api_endpoint:
        print(f"API Endpoint => {api_endpoint.value}")

if __name__ == "__main__":
    run_deploy()
