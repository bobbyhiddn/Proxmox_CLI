# commands/vm_list.py
import click
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@click.command()
@click.pass_context
def vm_list(ctx):
    """List all VMs and containers on the configured Proxmox node."""
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
    response.raise_for_status()

    ticket = response.json()['data']['ticket']
    cookies = {'PVEAuthCookie': ticket}

    # List QEMU VMs and LXC containers using the authenticated session
    vm_response = requests.get(
        f"https://{proxmox_ip}:8006/api2/json/nodes/{node}/qemu",
        cookies=cookies,
        verify=False
    )
    vm_response.raise_for_status()
    vms = vm_response.json()['data']
    container_response = requests.get(
        f"https://{proxmox_ip}:8006/api2/json/nodes/{node}/lxc",
        cookies=cookies,
        verify=False
    )
    container_response.raise_for_status()
    containers = container_response.json()['data']

    # Print VMs and containers
    click.echo(f"QEMU VMs on node {node}:")
    for vm in vms:
        click.echo(f"VM ID: {vm['vmid']}, Name: {vm.get('name', 'N/A')}, Status: {vm['status']}")
    click.echo(f"LXC containers on node {node}:")
    for container in containers:
        click.echo(f"Container ID: {container['vmid']}, Name: {container.get('name', 'N/A')}, Status: {container['status']}")

if __name__ == "__main__":
    vm_list()
