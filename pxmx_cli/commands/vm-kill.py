import click
import paramiko
import getpass

# Define the Click command
@click.command()
@click.argument('vm_ids', nargs=-1, required=True)
@click.pass_context
def vm_kill(ctx, vm_ids):
    """Kill VM(s) by ID and clean up logs."""
    config = ctx.obj
    proxmox_ip = config['proxmox_ip']
    username = 'root'
    password = getpass.getpass(f"Enter the password for {username}@{proxmox_ip}: ")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(proxmox_ip, username=username, password=password)

        for vm_id in vm_ids:
            click.echo(f"Processing VM {vm_id}...")
            commands = [
                f"echo 'Attempting to stop VM {vm_id}...' && qm stop {vm_id} && sleep 5",
                f"echo 'Removing lock file for VM {vm_id}...' && rm -f /var/lock/qemu-server/lock-{vm_id}.conf",
                f"echo 'Removing lock status from VM {vm_id} configuration...' && sed -i '/^lock:/d' /etc/pve/nodes/proxmox/qemu-server/{vm_id}.conf",
                f"echo 'Destroying VM {vm_id}...' && qm destroy {vm_id} && sleep 2",
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
            cleanup_logs = click.confirm("Do you want to clean up logs for this VM?")
            if cleanup_logs:
                _, stdout, stderr = ssh.exec_command(f"cp /var/log/pve/tasks/active /var/log/pve/tasks/active.backup && sed -i '/:qm[^:]*:{vm_id}:/d' /var/log/pve/tasks/active && echo 'Log cleanup for VM {vm_id} completed.'")
                click.echo(stdout.read().decode('utf-8'))
                error = stderr.read().decode('utf-8')
                if error:
                    click.echo(f"Error during log cleanup for VM {vm_id}: {error}")
            else:
                click.echo(f"Log cleanup for VM {vm_id} was not performed.")

            if error_occurred:
                click.echo(f"VM {vm_id} processing completed with errors.")
            else:
                click.echo(f"VM {vm_id} has been processed successfully.")

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