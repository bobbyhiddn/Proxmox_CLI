import click
import paramiko
import getpass

# Define the Click command
@click.command()
@click.argument('ct_ids', nargs=-1, required=True)
@click.pass_context
def ct_kill(ctx, ct_ids):
    """Kill container(s) by ID and clean up logs."""
    config = ctx.obj
    proxmox_ip = config['proxmox_ip']
    username = 'root'
    password = getpass.getpass(f"Enter the password for {username}@{proxmox_ip}: ")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(proxmox_ip, username=username, password=password)

        for ct_id in ct_ids:
            ct_id = ct_id.upper()
            if ct_id.startswith('CT'):
                ct_id = ct_id[2:]
                click.echo(f"Processing container {ct_id}...")

                # Check the container status
                _, stdout, _ = ssh.exec_command(f"pct status {ct_id}")
                status_output = stdout.read().decode('utf-8')
                click.echo(status_output)

                if 'status: stopped' in status_output:
                    click.echo(f"Container {ct_id} is already stopped.")
                else:
                    # Attempt to stop the container gracefully
                    click.echo(f"Attempting to stop container {ct_id}...")
                    _, stdout, stderr = ssh.exec_command(f"pct stop {ct_id}")
                    click.echo(stdout.read().decode('utf-8'))
                    error = stderr.read().decode('utf-8')

                    # Only force stop if graceful stop failed AND container is still running
                    if error and 'status: running' in status_output:
                        click.echo(f"Forcefully stopping container {ct_id}...")
                        _, stdout, stderr = ssh.exec_command(f"pct shutdown {ct_id} --force")
                        click.echo(stdout.read().decode('utf-8'))
                        error = stderr.read().decode('utf-8')

                        if error:
                            click.echo(f"Error forcefully stopping container {ct_id}: {error}")

                # Kill remaining processes and clean up
                commands = [
                    f"echo 'Killing container {ct_id} processes...' && pkill -9 -f 'lxc-start.*--name {ct_id}'",
                    f"echo 'Removing lock file for container {ct_id}...' && rm -f /var/lock/lxc/{ct_id}.lock",
                    f"echo 'Removing lock status from container {ct_id} configuration...' && sed -i '/^lock:/d' /etc/pve/nodes/proxmox/lxc/{ct_id}.conf",
                    f"echo 'Destroying container {ct_id}...' && pct destroy {ct_id} --purge --force && sleep 2",
                ]

                error_occurred = False
                for command in commands:
                    _, stdout, stderr = ssh.exec_command(command)
                    click.echo(stdout.read().decode('utf-8'))
                    error = stderr.read().decode('utf-8')
                    if error:
                        error_occurred = True
                        click.echo(f"Error executing command '{command}': {error}")

            else:
                click.echo(f"Invalid prefix for ID: {ct_id}. Must be formatted as CT###. Skipping...")
                continue

            # Ask if the user wants to clean logs regardless of errors
            cleanup_logs = click.confirm(f"Do you want to clean up logs for container {ct_id}?")
            if cleanup_logs:
                _, stdout, stderr = ssh.exec_command(f"cp /var/log/pve/tasks/active /var/log/pve/tasks/active.backup && sed -i '/:pct[^:]*:{ct_id}:/d' /var/log/pve/tasks/active && echo 'Log cleanup for container {ct_id} completed.'")
                click.echo(stdout.read().decode('utf-8'))
                error = stderr.read().decode('utf-8')
                if error:
                    click.echo(f"Error during log cleanup for container {ct_id}: {error}")
            else:
                click.echo(f"Log cleanup for container {ct_id} was not performed.")

            if error_occurred:
                click.echo(f"Container {ct_id} processing completed with errors.")
            else:
                click.echo(f"Container {ct_id} has been removed successfully.")

    except paramiko.AuthenticationException:
        click.echo("Authentication failed, please verify your credentials.")
    except paramiko.SSHException as e:
        click.echo(f"Error establishing SSH connection: {e}")
    except Exception as e:
        click.echo(f"An error occurred: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    ct_kill()