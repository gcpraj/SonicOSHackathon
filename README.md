# SONiC Network Topology with Dual Paths

This project creates a 6-container SONiC network topology using Docker Compose with the following layout:

```
    A
   / \
  B   E
  |   |
  C   F
   \ /
    D
```

## Topology Description

- **Path 1**: A -> B -> C -> D
- **Path 2**: A -> E -> F -> D
- **Dual paths** from container A to container D for redundancy
- **Management network** shared across all containers (172.20.0.0/16)
- **Data interfaces** without IP addresses (handled by SONiC internally)

## Container Details

| Container | Hostname | Management IP | SSH Port | REST Port | gNMI Port | Telnet Port |
|-----------|----------|---------------|----------|-----------|-----------|-------------|
| sonic-a   | sonic-a  | 172.20.0.10   | 2201     | 8001      | 9001      | 2301        |
| sonic-b   | sonic-b  | 172.20.0.20   | 2202     | 8002      | 9002      | 2302        |
| sonic-c   | sonic-c  | 172.20.0.30   | 2203     | 8003      | 9003      | 2303        |
| sonic-d   | sonic-d  | 172.20.0.40   | 2204     | 8004      | 9004      | 2304        |
| sonic-e   | sonic-e  | 172.20.0.50   | 2205     | 8005      | 9005      | 2305        |
| sonic-f   | sonic-f  | 172.20.0.60   | 2206     | 8006      | 9006      | 2306        |

## Features Enabled

- **FRR with BGP**: Enabled on all containers
- **SSH**: Port forwarding configured for remote access
- **REST API**: HTTP and HTTPS endpoints available
- **gNMI**: gRPC Network Management Interface
- **Telnet**: Legacy access method
- **LLDP**: Link Layer Discovery Protocol
- **SNMP**: Simple Network Management Protocol
- **Telemetry**: Network monitoring and analytics

## Prerequisites

1. Docker and Docker Compose installed
2. `docker-sonic-vs` image available locally
3. Sufficient system resources (6 containers)

## Quick Start

1. **Start the topology**:
   ```bash
   docker-compose up -d
   ```

2. **Check container status**:
   ```bash
   docker-compose ps
   ```

3. **Access containers via SSH**:
   ```bash
   # Example: Access container A
   ssh admin@localhost -p 2201
   ```

4. **Stop the topology**:
   ```bash
   docker-compose down
   ```

## Network Configuration

### Management Network
- **Subnet**: 172.20.0.0/16
- **Purpose**: Out-of-band management access
- **Gateway**: 172.20.0.1

### Data Networks
- **link_a_b**: Connects sonic-a and sonic-b
- **link_b_c**: Connects sonic-b and sonic-c
- **link_c_d**: Connects sonic-c and sonic-d
- **link_a_e**: Connects sonic-a and sonic-e
- **link_e_f**: Connects sonic-e and sonic-f
- **link_f_d**: Connects sonic-f and sonic-d

All data networks are internal bridges without external connectivity.

## Configuration Files

Each container has its own configuration directory under `configs/sonic-[a-f]/`:
- `config_db.json`: Main SONiC configuration database

## Common Operations

### Viewing Logs
```bash
# All containers
docker-compose logs

# Specific container
docker-compose logs sonic-a
```

### Executing Commands
```bash
# Enter container shell
docker exec -it sonic-a bash

# Run SONiC CLI
docker exec -it sonic-a sonic-cli
```

### BGP Configuration
After containers are running, you can configure BGP using the SONiC CLI or vtysh as needed.

## Troubleshooting

1. **Container startup issues**: Check `docker-compose logs [container-name]`
2. **Network connectivity**: Verify bridge networks with `docker network ls`
3. **Port conflicts**: Ensure ports 2201-2206, 8001-8006, 9001-9006, 2301-2306 are available
4. **Resource constraints**: Monitor system resources with `docker stats`

## Advanced Configuration

### Enabling Additional Features
Modify the `FEATURE` section in `config_db.json` files to enable/disable SONiC features.

### Custom BGP Configuration
Configure BGP using the SONiC CLI after startup as needed for your specific requirements.

### Persistent Storage
Add volume mappings to the docker-compose.yml for persistent configuration storage.

## Security Notes

- Default credentials may be admin/admin or admin/YourPaSsWoRd
- Change default passwords in production environments
- Consider network security policies for exposed ports
- Use proper authentication mechanisms for production deployments

## License

This configuration is provided for educational and testing purposes.
