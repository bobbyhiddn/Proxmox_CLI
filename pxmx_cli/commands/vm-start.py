import click
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@click.command()
@click.argument('vm_id', required=True)
@click.pass_context
def vm_start(ctx, vm_id):
    """Start a VM by ID."""
    config = ctx.obj
    proxmox_ip = config['proxmox_ip']
    username = config['username']
    password = config['password']  # Assuming password is safely handled
    node = config.get('node', 'proxmox')  # Default node name if not specified in config

    # Authenticate and obtain a ticket
    response = requests.post(
        f"https://{proxmox_ip}:8006/api2/json/access/ticket",
        data={"username": username, "password": password},
        verify=False  # SSL verification is disabled, not recommended for production
    )
    response.raise_for_status()  # Raise an error for bad responses

    ticket = response.json()['data']['ticket']
    csrf_token = response.json()['data']['CSRFPreventionToken']

    cookies = {'PVEAuthCookie': ticket}
    headers = {'CSRFPreventionToken': csrf_token}

    vm_id = vm_id.upper()
    if vm_id.startswith('VM'):
        vm_id = vm_id[2:]
        click.echo(f"Processing VM {vm_id}...")

        # Start the VM using the Proxmox API
        response = requests.post(
            f"https://{proxmox_ip}:8006/api2/json/nodes/{node}/qemu/{vm_id}/status/start",
            cookies=cookies,
            headers=headers,
            verify=False
        )

        if response.status_code == 200:
            click.echo(f"VM {vm_id} has been started successfully.")
        else:
            click.echo(f"Error starting VM {vm_id}:")
            click.echo(f"Status Code: {response.status_code}")
            click.echo(f"Error Message: {response.text}")
    else:
        click.echo(f"Invalid prefix for ID: {vm_id}. Must be formatted as VM###.")

if __name__ == '__main__':
    vm_start()