import requests
import getpass

def list_vms_and_containers(proxmox_ip, username, node):
    password = getpass.getpass("Enter the Proxmox API password: ")

    # Authenticate and obtain a ticket
    response = requests.post(
        f"https://{proxmox_ip}:8006/api2/json/access/ticket",
        data={"username": username, "password": password},
        verify=False  # NOTE: For production, handle SSL certificates properly
    )
    response.raise_for_status()  # Raise an error for bad responses

    ticket = response.json()['data']['ticket']

    cookies = {'PVEAuthCookie': ticket}

    # List QEMU VMs on a specific Proxmox node
    print(f"Listing QEMU VMs on node {node}...")
    vm_response = requests.get(
        f"https://{proxmox_ip}:8006/api2/json/nodes/{node}/qemu",
        cookies=cookies,
        verify=False
    )
    vm_response.raise_for_status()

    vms = vm_response.json()['data']
    for vm in vms:
        print(f"VM ID: {vm['vmid']}, Name: {vm.get('name', 'N/A')}, Status: {vm['status']}")

    # List LXC containers on the same node
    print(f"Listing LXC containers on node {node}...")
    container_response = requests.get(
        f"https://{proxmox_ip}:8006/api2/json/nodes/{node}/lxc",
        cookies=cookies,
        verify=False
    )
    container_response.raise_for_status()

    containers = container_response.json()['data']
    for container in containers:
        print(f"Container ID: {container['vmid']}, Name: {container.get('name', 'N/A')}, Status: {container['status']}")

if __name__ == "__main__":
    proxmox_ip = "192.168.0.128"  # Set the Proxmox server IP address
    username = "root@pam"  # Set the Proxmox server username
    node = "proxmox"  # Set the node name
    list_vms_and_containers(proxmox_ip, username, node)
