import click
import paramiko
import getpass

# Define the Click command
@click.command()
@click.argument('vm_or_ct_ids', nargs=-1, required=True)
@click.pass_context
def vm_kill(ctx, vm_or_ct_ids):
    """Kill VM(s) or container(s) by ID and clean up logs."""
    config = ctx.obj
    proxmox_ip = config['proxmox_ip']
    username = 'root'
    password = getpass.getpass(f"Enter the password for {username}@{proxmox_ip}: ")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(proxmox_ip, username=username, password=password)

        for vm_or_ct_id in vm_or_ct_ids:
            if vm_or_ct_id.startswith('VM'):
                vm_id = vm_or_ct_id[2:]
                click.echo(f"Processing VM {vm_id}...")
                stop_command = f"qm stop {vm_id}"
                lock_file = f"/var/lock/qemu-server/lock-{vm_id}.conf"
                config_file = f"/etc/pve/nodes/proxmox/qemu-server/{vm_id}.conf"
                destroy_command = f"qm destroy {vm_id}"
            elif vm_or_ct_id.startswith('CT'):
                ct_id = vm_or_ct_id[2:]
                click.echo(f"Processing container {ct_id}...")
                stop_command = f"pct stop {ct_id}"
                lock_file = f"/var/lock/lxc/{ct_id}.lock"
                config_file = f"/etc/pve/nodes/proxmox/lxc/{ct_id}.conf"
                destroy_command = f"pct destroy {ct_id}"
            else:
                click.echo(f"Invalid prefix for ID: {vm_or_ct_id}. Skipping...")
                continue

            commands = [
                f"echo 'Attempting to stop {vm_or_ct_id}...' && {stop_command} && sleep 5",
                f"echo 'Removing lock file for {vm_or_ct_id}...' && rm -f {lock_file}",
                f"echo 'Removing lock status from {vm_or_ct_id} configuration...' && sed -i '/^lock:/d' {config_file}",
                f"echo 'Destroying {vm_or_ct_id}...' && {destroy_command} && sleep 2",
            ]

            error_occurred = False
            for command in commands:
                _, stdout, stderr = ssh.exec_command(command)
                click.echo(stdout.read().decode('utf-8'))
                error = stderr.read().decode('utf-8')
                if error:
                    error_occurred = True
                    click.echo(f"Error executing command '{command}': {error}")

            # Ask if the user wants to clean logs regardless of errors
            cleanup_logs = click.confirm(f"Do you want to clean up logs for {vm_or_ct_id}?")
            if cleanup_logs:
                _, stdout, stderr = ssh.exec_command(f"cp /var/log/pve/tasks/active /var/log/pve/tasks/active.backup && sed -i '/:qm[^:]*:{vm_id}:/d' /var/log/pve/tasks/active && echo 'Log cleanup for {vm_or_ct_id} completed.'")
                click.echo(stdout.read().decode('utf-8'))
                error = stderr.read().decode('utf-8')
                if error:
                    click.echo(f"Error during log cleanup for {vm_or_ct_id}: {error}")
            else:
                click.echo(f"Log cleanup for {vm_or_ct_id} was not performed.")

            if error_occurred:
                click.echo(f"{vm_or_ct_id} processing completed with errors.")
            else:
                click.echo(f"{vm_or_ct_id} has been removed successfully.")

    except paramiko.AuthenticationException:
        click.echo("Authentication failed, please verify your credentials.")
    except paramiko.SSHException as e:
        click.echo(f"Error establishing SSH connection: {e}")
    except Exception as e:
        click.echo(f"An error occurred: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    vm_kill()