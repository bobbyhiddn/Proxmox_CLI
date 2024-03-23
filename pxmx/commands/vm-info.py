import requests
import getpass

def get_vm_info(proxmox_ip, username, vm_id):
    password = getpass.getpass("Enter the Proxmox API password: ")

    # Authenticate and obtain a ticket
    response = requests.post(
        f"https://{proxmox_ip}:8006/api2/json/access/ticket",
        data={"username": username, "password": password},
        verify=False
    )
    response.raise_for_status()  # Raise an error for bad responses

    data = response.json()
    ticket = data['data']['ticket']
    csrf_token = data['data']['CSRFPreventionToken']

    cookies = {'PVEAuthCookie': ticket}
    headers = {'CSRFPreventionToken': csrf_token}

    # Assuming NODE variable is set or hardcoded here
    node = "proxmox"  # Adjust the node name as necessary

    # Get information for the specific VM by VM_ID
    vm_info_response = requests.get(
        f"https://{proxmox_ip}:8006/api2/json/nodes/{node}/qemu/{vm_id}/status/current",
        cookies=cookies,
        verify=False
    )
    vm_info_response.raise_for_status()

    vm_info = vm_info_response.json()['data']
    print(f"VM Status: {vm_info['status']}")
    print(f"VM CPU Usage: {vm_info['cpu']}")
    print(f"VM Memory Usage: {vm_info['mem']}")

    # Fetch the VM agent network interface information
    vm_agent_info_response = requests.get(
        f"https://{proxmox_ip}:8006/api2/json/nodes/{node}/qemu/{vm_id}/agent/network-get-interfaces",
        cookies=cookies,
        verify=False
    )
    vm_agent_info_response.raise_for_status()

    vm_agent_info = vm_agent_info_response.json()['data']['result']
    print("Raw VM agent network interface information:")
    print(vm_agent_info)

    # Extract and print IP addresses
    for interface in vm_agent_info:
        if interface['name'] != "lo":
            for ip_info in interface.get("ip-addresses", []):
                if ip_info["ip-address-type"] == "ipv4":
                    print(f"VM IP Address: {ip_info['ip-address']}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py VM_ID")
        sys.exit(1)
    vm_id = sys.argv[1]
    proxmox_ip = "192.168.0.128"  # Set the Proxmox server IP address
    username = "root@pam"  # Set the Proxmox server username
    get_vm_info(proxmox_ip, username, vm_id)
