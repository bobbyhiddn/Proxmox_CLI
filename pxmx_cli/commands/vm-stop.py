import click
import requests
import paramiko
import getpass
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define the Click command
@click.command()
@click.argument('vm_id', required=True)
@click.option('--force', is_flag=True, help='Delete the lock file before stopping the VM.')
@click.pass_context
def vm_stop(ctx, vm_id, force):
    """Stop a VM by ID."""
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

        if force:
            # Delete the lock file using paramiko
            ssh_username = 'root'
            ssh_password = getpass.getpass(f"Enter the SSH password for {ssh_username}@{proxmox_ip}: ")

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                ssh.connect(proxmox_ip, username=ssh_username, password=ssh_password)
                click.echo(f"Deleting lock file for VM {vm_id}...")
                ssh.exec_command(f"rm -f /var/lock/qemu-server/lock-{vm_id}.conf")
            except Exception as e:
                click.echo(f"Error deleting lock file: {e}")
            finally:
                ssh.close()

        # Stop the VM using the Proxmox API
        response = requests.post(
            f"https://{proxmox_ip}:8006/api2/json/nodes/{node}/qemu/{vm_id}/status/stop",
            cookies=cookies,
            headers=headers,
            verify=False
        )

        if response.status_code == 200:
            click.echo(f"VM {vm_id} has been stopped successfully.")
        else:
            click.echo(f"Error stopping VM {vm_id}:")
            click.echo(f"Status Code: {response.status_code}")
            click.echo(f"Error Message: {response.text}")
    else:
        click.echo(f"Invalid prefix for ID: {vm_id}. Must be formatted as VM###.")

if __name__ == '__main__':
    vm_stop()