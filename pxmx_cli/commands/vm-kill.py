import click
import paramiko

@click.command()
@click.argument('vm_ids', nargs=-1, required=True)
@click.pass_context
def vm_kill(ctx, vm_ids):
    """Kill VM(s) by ID."""
    config = ctx.obj
    proxmox_ip = config['proxmox_ip']
    username = config['username']
    password = config['password']  # Assuming password is safely handled

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(proxmox_ip, username=username, password=password)

        for vm_id in vm_ids:
            click.echo(f"Processing VM {vm_id}...")

            # Check if VM exists
            stdin, stdout, stderr = ssh.exec_command(f"qm list | grep -qw '{vm_id}'")
            if stderr.read().decode('utf-8'):
                click.echo(f"VM {vm_id} does not exist.")
                continue  # Skip to the next VM ID if the current one does not exist

            # Proceed with VM killing steps
            commands = [
                f"rm -f /var/lock/qemu-server/lock-{vm_id}.conf",
                f"qm stop {vm_id}",
                f"sed -i '/^lock:/d' /etc/pve/nodes/proxmox/qemu-server/{vm_id}.conf",
                f"qm destroy {vm_id}"
            ]

            for command in commands:
                stdin, stdout, stderr = ssh.exec_command(command)
                error = stderr.read().decode('utf-8')
                if error:
                    raise Exception(f"Error executing command '{command}': {error}")

            click.echo(f"VM {vm_id} has been destroyed.")

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
