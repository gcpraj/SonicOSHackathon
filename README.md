# SONiC Network Topology with Dual Paths

This project creates a 6-container SONiC network topology using Docker Compose with the following layout:

```
    1
   / \
  2   5
  |   |
  3   6
   \ /
    4
```

## Topology Description

- **Path 1**: sonic-1 -> sonic-2 -> sonic-3 -> sonic-4
- **Path 2**: sonic-1 -> sonic-5 -> sonic-6 -> sonic-4
- **Dual paths** from sonic-1 to sonic-4 for redundancy
- **Management network** shared across all containers (172.20.0.0/16)
- **Data interfaces** with structured IP addressing scheme

## Container Details

| Container | Hostname | Management IP | SSH Port | REST Port | gNMI Port | Telnet Port |
|-----------|----------|---------------|----------|-----------|-----------|-------------|
| sonic-1   | sonic-1  | 172.20.0.11   | 2201     | 8001      | 9001      | 2301        |
| sonic-2   | sonic-2  | 172.20.0.12   | 2202     | 8002      | 9002      | 2302        |
| sonic-3   | sonic-3  | 172.20.0.13   | 2203     | 8003      | 9003      | 2303        |
| sonic-4   | sonic-4  | 172.20.0.14   | 2204     | 8004      | 9004      | 2304        |
| sonic-5   | sonic-5  | 172.20.0.15   | 2205     | 8005      | 9005      | 2305        |
| sonic-6   | sonic-6  | 172.20.0.16   | 2206     | 8006      | 9006      | 2306        |

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
4. Python 3.8 or higher for testing framework
5. Git for version control

## Quick Start

### 1. Set up the Python testing environment

Set up the Python virtual environment with pyATS for network testing:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 2. Start the SONiC topology

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
   # Example: Access sonic-1
   ssh admin@localhost -p 2201
   
   # Access other containers
   ssh admin@localhost -p 2202  # sonic-2
   ssh admin@localhost -p 2203  # sonic-3
   ssh admin@localhost -p 2204  # sonic-4
   ssh admin@localhost -p 2205  # sonic-5
   ssh admin@localhost -p 2206  # sonic-6
   ```

### 3. Run network tests

With the SONiC topology running, you can execute automated tests:

```bash
# Activate the Python environment (if not already active)
source venv/bin/activate

# Run the test suite with testbed
python tests/sonic_network_test.py --testbed testbed.yaml

# Run without testbed (basic mode)
python tests/sonic_network_test.py
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
- **Container IPs**: 172.20.0.11 - 172.20.0.16

### Data Networks

The data networks use a structured IP addressing scheme: `192.X.Y.Z`
- **X**: Lower node index
- **Y**: Higher node index  
- **Z**: 10 + node index (11-16)
- **Subnet**: /24 for each link

| Network | Subnet | Connected Containers | IP Assignments |
|---------|--------|---------------------|----------------|
| link_1_2 | 192.1.2.0/24 | sonic-1 ↔ sonic-2 | sonic-1: 192.1.2.11<br>sonic-2: 192.1.2.12 |
| link_2_3 | 192.2.3.0/24 | sonic-2 ↔ sonic-3 | sonic-2: 192.2.3.12<br>sonic-3: 192.2.3.13 |
| link_3_4 | 192.3.4.0/24 | sonic-3 ↔ sonic-4 | sonic-3: 192.3.4.13<br>sonic-4: 192.3.4.14 |
| link_1_5 | 192.1.5.0/24 | sonic-1 ↔ sonic-5 | sonic-1: 192.1.5.11<br>sonic-5: 192.1.5.15 |
| link_5_6 | 192.5.6.0/24 | sonic-5 ↔ sonic-6 | sonic-5: 192.5.6.15<br>sonic-6: 192.5.6.16 |
| link_6_4 | 192.4.6.0/24 | sonic-6 ↔ sonic-4 | sonic-6: 192.4.6.16<br>sonic-4: 192.4.6.14 |

All data networks are internal bridges without external connectivity.

## Configuration Files

Each container has its own configuration directory under `configs/sonic-[1-6]/`:
- `config_db.json`: Main SONiC configuration database
- `bgpd.conf`: FRR BGP configuration (where applicable)
- `startup.sh`: Container startup script
- Other SONiC configuration files

## Common Operations

### Viewing Logs
```bash
# All containers
docker-compose logs

# Specific container
docker-compose logs sonic-1
```

### Executing Commands
```bash
# Enter container shell
docker exec -it sonic-1 bash

# Run SONiC CLI
docker exec -it sonic-1 sonic-cli
```

### Network Connectivity Testing

#### Manual Testing
```bash
# Test connectivity between containers via data links
docker exec -it sonic-1 ping 192.1.2.12  # sonic-1 to sonic-2
docker exec -it sonic-2 ping 192.2.3.13  # sonic-2 to sonic-3
docker exec -it sonic-1 ping 192.1.5.15  # sonic-1 to sonic-5 (alternate path)
```

#### Automated Testing with pyATS
```bash
# Run all network tests
source venv/bin/activate
python tests/sonic_network_test.py --testbed testbed.yaml

# View test results in terminal output
```

## Python Testing Framework

This project includes a comprehensive Python testing framework using **pyATS** (Python Automated Test Systems), Cisco's testing framework designed for network automation and validation.

### Testing Components

1. **pyATS Framework**: Enterprise-grade testing framework for network devices
2. **Test Scripts**: Located in `tests/` directory
3. **Testbed Configuration**: `testbed.yaml` defines the network topology

### Virtual Environment Management

The project uses a Python virtual environment to isolate dependencies:

- **Virtual Environment**: `venv/` (excluded from git)
- **Requirements**: `requirements.txt` (production) and `requirements-dev.txt` (development)

### For New Team Members

```bash
# Clone the repository
git clone <repository-url>
cd SonicOSHackathon

# Set up the Python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Start the SONiC topology
docker-compose up -d

# Run tests
python tests/sonic_network_test.py --testbed testbed.yaml
```

### Test Categories

- **Connectivity Tests**: Verify device reachability and network links
- **Configuration Tests**: Validate BGP, interface, and protocol configurations
- **Topology Tests**: Ensure proper network topology and redundant paths
- **Performance Tests**: Monitor network performance metrics (can be extended)

### Adding New Tests

1. Create test scripts in `tests/` directory following pyATS format
2. Update `testbed.yaml` if new devices/connections are added
3. Add new test methods to existing test classes
4. Update requirements if new Python packages are needed

### BGP Configuration
After containers are running, you can configure BGP using the SONiC CLI or vtysh as needed.

## Troubleshooting

### Docker and Container Issues
1. **Container startup issues**: Check `docker-compose logs [container-name]`
2. **Network connectivity**: Verify bridge networks with `docker network ls`
3. **Port conflicts**: Ensure ports 2201-2206, 8001-8006, 9001-9006, 2301-2306 are available
4. **Resource constraints**: Monitor system resources with `docker stats`

### Python Testing Issues
1. **Virtual environment not found**: Create it with `python3 -m venv venv`
2. **Package installation errors**: Update pip with `pip install --upgrade pip`
3. **pyATS test failures**: Check testbed.yaml configuration and container connectivity
4. **Path issues**: Ensure you're in the project root directory when running commands

### Common Python Environment Commands
```bash
# Check if virtual environment is active
which python  # Should show path to venv/bin/python

# Reinstall requirements
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Reset virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

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
