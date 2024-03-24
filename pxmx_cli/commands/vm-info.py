import click
import requests

@click.command()
@click.argument('vm_id', required=True)
@click.pass_context
def vm_info(ctx, vm_id):
    """Retrieve information about a specific VM."""
    config = ctx.obj
    vm_id = vm_id.upper()
    proxmox_ip = config['proxmox_ip']
    username = config['username']
    password = config['password']  # Assuming password is safely handled

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

    # Assuming NODE variable is set or hardcoded here, or obtained from config
    node = config.get('node', 'proxmox')  # Adjust the node name as necessary

    # Get information for the specific VM by VM_ID
    vm_info_response = requests.get(
        f"https://{proxmox_ip}:8006/api2/json/nodes/{node}/qemu/{vm_id}/status/current",
        cookies=cookies,
        verify=False
    )
    vm_info_response.raise_for_status()

    vm_info = vm_info_response.json()['data']
    click.echo(f"VM Status: {vm_info['status']}")
    click.echo(f"VM CPU Usage: {vm_info['cpu']}")
    click.echo(f"VM Memory Usage: {vm_info['mem']}")

    # Fetch the VM agent network interface information
    vm_agent_info_response = requests.get(
        f"https://{proxmox_ip}:8006/api2/json/nodes/{node}/qemu/{vm_id}/agent/network-get-interfaces",
        cookies=cookies,
        verify=False
    )
    vm_agent_info_response.raise_for_status()

    vm_agent_info = vm_agent_info_response.json()['data']['result']
    click.echo("Raw VM agent network interface information:")
    click.echo(vm_agent_info)

    # Extract and print IP addresses
    for interface in vm_agent_info:
        if interface['name'] != "lo":
            for ip_info in interface.get("ip-addresses", []):
                if ip_info["ip-address-type"] == "ipv4":
                    click.echo(f"VM IP Address: {ip_info['ip-address']}")

if __name__ == "__main__":
    vm_info()
