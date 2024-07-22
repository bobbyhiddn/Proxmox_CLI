# Proxmox CLI (pxmx-cli)

A Python-based command-line interface for managing Proxmox VE servers.

## Features

- List VMs and containers
- Start and stop VMs
- Clone VMs
- Retrieve VM information
- Kill VMs and containers (with cleanup)
- Configuration management

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourgithub/Proxmox_CLI.git
   cd Proxmox_CLI
   ```

2. Install the package:
   ```
   pip install .
   ```

## Configuration

On first run, the CLI will prompt you to enter your Proxmox server details:

- Proxmox IP or hostname
- API username
- Password

This information is stored in `~/.pxmx` for future use.

## Usage

After installation, you can use the `pxmx` command to interact with your Proxmox server:

```
pxmx [COMMAND] [OPTIONS]
```

Available commands:

- `vm-list`: List all VMs and containers
- `vm-start`: Start a VM
- `vm-stop`: Stop a VM
- `vm-clone`: Clone a VM
- `vm-info`: Get information about a VM
- `vm-kill`: Force stop and remove a VM
- `ct-kill`: Force stop and remove a container
- `config`: Display current configuration
- `pxmx`: Display available commands and aliases

For detailed information on each command, use:

```
pxmx [COMMAND] --help
```

## Examples

List all VMs and containers:
```
pxmx vm-list
```

Start a VM:
```
pxmx vm-start VM101
```

Stop a VM:
```
pxmx vm-stop VM101
```

Clone a VM:
```
pxmx vm-clone VM101 --name new-vm-name
```

Get VM information:
```
pxmx vm-info VM101
```

Force stop and remove a VM:
```
pxmx vm-kill VM101
```

## Security Note

This CLI stores your Proxmox credentials in plain text in the `~/.pxmx` file. Ensure that this file has appropriate permissions and consider using API tokens instead of passwords for enhanced security.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.