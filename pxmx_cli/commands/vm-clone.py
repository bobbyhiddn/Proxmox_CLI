import click
import requests
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@click.command()
@click.argument('vm_id', required=True)
@click.option('--name', help='Name of the cloned VM (alphanumeric, hyphens, and uppercase/lowercase letters only)')
@click.pass_context
def vm_clone(ctx, vm_id, name):
    """Clone a VM by ID."""
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

        # Check if the VM is stopped
        vm_status_response = requests.get(
            f"https://{proxmox_ip}:8006/api2/json/nodes/{node}/qemu/{vm_id}/status/current",
            cookies=cookies,
            headers=headers,
            verify=False
        )
        vm_status = vm_status_response.json()['data']['status']

        if vm_status != 'stopped':
            click.echo(f"VM {vm_id} is not stopped. Please stop the VM before cloning.")
            return

        # Prompt for the VM name if not provided
        if not name:
            while True:
                name = click.prompt("Enter the name of the cloned VM")
                if re.match(r'^[a-zA-Z0-9-]+$', name):
                    break
                click.echo("Invalid VM name. Only alphanumeric characters, hyphens, and uppercase/lowercase letters are allowed.")

        # Fetch the next available VM ID
        vm_list_response = requests.get(
            f"https://{proxmox_ip}:8006/api2/json/nodes/{node}/qemu",
            cookies=cookies,
            headers=headers,
            verify=False
        )
        vm_list = vm_list_response.json()['data']
        vm_ids = [vm['vmid'] for vm in vm_list]
        new_id = max(vm_ids) + 1

        # Clone the VM using the Proxmox API
        clone_data = {
            'newid': new_id,
            'name': name,
        }
        response = requests.post(
            f"https://{proxmox_ip}:8006/api2/json/nodes/{node}/qemu/{vm_id}/clone",
            cookies=cookies,
            headers=headers,
            data=clone_data,
            verify=False
        )

        if response.status_code == 200:
            click.echo(f"VM {vm_id} has been cloned successfully with ID {new_id}.")
        else:
            click.echo(f"Error cloning VM {vm_id}:")
            click.echo(f"Status Code: {response.status_code}")
            click.echo(f"Error Message: {response.text}")
    else:
        click.echo(f"Invalid prefix for ID: {vm_id}. Must be formatted as VM###.")

if __name__ == '__main__':
    vm_clone()