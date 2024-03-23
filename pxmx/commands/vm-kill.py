import paramiko
import getpass
import sys

PROXMOX_IP = "192.168.0.128"
USERNAME = "root"

def execute_ssh_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    if error:
        raise Exception(f"Error executing command '{command}': {error}")
    return output

def main(vm_ids):
    password = getpass.getpass(f"Enter the SSH password for {USERNAME}@{PROXMOX_IP}: ")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(PROXMOX_IP, username=USERNAME, password=password)

    for vm_id in vm_ids:
        print(f"Processing VM {vm_id}...")

        # Check if VM exists
        vm_exists_command = f"qm list | grep -qw '{vm_id}'"
        try:
            execute_ssh_command(ssh, vm_exists_command)
            print(f"VM {vm_id} exists. Proceeding with further actions...")
        except Exception as e:
            print(e)
            continue  # Skip to the next VM ID if current one does not exist

        # Remove lock file
        remove_lock_file_command = f"rm -f /var/lock/qemu-server/lock-{vm_id}.conf"
        execute_ssh_command(ssh, remove_lock_file_command)
        print(f"Lock file removed for VM {vm_id}.")

        # Attempt to stop the VM gracefully
        stop_vm_command = f"qm stop {vm_id}"
        execute_ssh_command(ssh, stop_vm_command)
        print(f"VM {vm_id} stop attempted.")

        # Remove the lock line from VM configuration
        config_file = f"/etc/pve/nodes/proxmox/qemu-server/{vm_id}.conf"
        remove_lock_status_command = f"sed -i '/^lock:/d' {config_file}"
        execute_ssh_command(ssh, remove_lock_status_command)
        print(f"Lock status removed from VM {vm_id} configuration.")

        # Destroy the VM
        destroy_vm_command = f"qm destroy {vm_id}"
        execute_ssh_command(ssh, destroy_vm_command)
        print(f"VM {vm_id} destroyed.")

    ssh.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py VMID [VMID...]")
        sys.exit(1)
    main(sys.argv[1:])
