#!/usr/bin/env python3
"""
Sample pyATS test script for SONiC network topology testing

This script demonstrates basic connectivity testing for the SONiC network
topology using pyATS fram                # Execute ping command from source to destination
                # Exit vtysh to run system ping, then re-enter
                source_device.execute('exit')  # Exit vtysh
                ping_command = f"ping -c 3 -W 2 {dst_ip}"
                logger.info(f"  Executing: {ping_command}")
                
                try:
                    ping_output = source_device.execute(ping_command)
                    source_device.execute('vtysh')  # Re-enter vtysh
                    
                    # Check if ping was successful (look for "3 received" or "0% packet loss")
                    if "3 received" in ping_output or "0% packet loss" in ping_output:"
"""
import logging
import yaml
from pyats import aetest
from pyats.log.utils import banner
from pyats.topology import Testbed, loader

# Configure logging
logger = logging.getLogger(__name__)

# Global testbed object - will be initialized before tests run
global_testbed = None

class CommonSetup(aetest.CommonSetup):
    """Common setup tasks for all test cases"""
    
    @aetest.subsection
    def load_testbed(self, testbed):
        """Store the testbed object globally for all test methods"""
        global global_testbed
        
        logger.info(banner("Setting up global testbed object"))
        
        # Store testbed globally
        global_testbed = testbed
        
        logger.info(f"Testbed available with {len(testbed.devices)} devices")
        for device_name, device in testbed.devices.items():
            logger.info(f"  Device: {device_name} ({device.os})")
            
        self.passed(f"Testbed setup complete - {len(testbed.devices)} devices available")
    
    @aetest.subsection
    def check_topology(self):
        """Check if testbed is properly defined"""
        global global_testbed
        
        logger.info(banner("Checking testbed topology"))
        
        # Verify testbed is loaded
        assert global_testbed is not None, "Testbed not loaded"
        assert global_testbed.devices, "No devices found in testbed"
        
        # Log available devices
        for device_name, device in global_testbed.devices.items():
            logger.info(f"Found device: {device_name}")
            logger.info(f"  Type: {device.type}")
            logger.info(f"  OS: {device.os}")
            logger.info(f"  Connections: {list(device.connections.keys())}")
            
        self.passed(f"Testbed validation passed - found {len(global_testbed.devices)} devices")
    
    @aetest.subsection
    def test_vtysh_connections(self):
        """Test connecting to all devices using vtysh (default connection)"""
        global global_testbed
        
        logger.info(banner("Testing VTYsh connections"))
        
        # Verify testbed is available
        assert global_testbed is not None, "Testbed not loaded"
        
        connection_results = []
        
        for device_name, device in global_testbed.devices.items():
            logger.info(f"Testing VTYsh connection to {device_name}")
            
            try:
                # 1. Connect to the device using default (vtysh) connection
                logger.info(f"  Connecting to {device_name} with VTYsh...")
                device.connect(via='default')
                
                # 2. Verify connection is established
                if device.connected:
                    logger.info(f"  ✓ Successfully connected to {device_name} via VTYsh")
                else:
                    raise Exception(f"VTYsh connection failed to {device_name}")
                
                # 3. Test VTYsh command execution
                logger.info(f"  Testing VTYsh command execution...")
                try:
                    # Execute a VTYsh command to verify device responsiveness
                    output = device.execute('show version')
                    logger.info(f"  ✓ VTYsh command execution successful on {device_name}")
                    logger.info(f"  Command output length: {len(output)} characters")
                except Exception as cmd_error:
                    logger.warning(f"  ⚠ VTYsh command execution failed on {device_name}: {cmd_error}")
                    # Don't fail the test for command issues, just log it
                
                # 4. Disconnect from the device
                logger.info(f"  Disconnecting from {device_name}...")
                device.disconnect()
                
                # 5. Verify connection is properly closed
                if not device.connected:
                    logger.info(f"  ✓ Successfully disconnected from {device_name}")
                    connection_results.append((device_name, True, "VTYsh Success"))
                else:
                    raise Exception(f"VTYsh disconnect failed for {device_name}")
                    
            except Exception as e:
                logger.error(f"  ✗ VTYsh connection test failed for {device_name}: {str(e)}")
                connection_results.append((device_name, False, str(e)))
        
        # Evaluate overall results
        failed_devices = [name for name, success, msg in connection_results if not success]
        successful_devices = [name for name, success, msg in connection_results if success]
        
        logger.info(f"VTYsh connection test summary:")
        logger.info(f"  ✓ Successful: {len(successful_devices)} devices: {', '.join(successful_devices)}")
        if failed_devices:
            logger.error(f"  ✗ Failed: {len(failed_devices)} devices: {', '.join(failed_devices)}")
        
        if failed_devices:
            self.failed(f"VTYsh connection tests failed for {len(failed_devices)} devices: {', '.join(failed_devices)}")
        else:
            self.passed(f"All {len(successful_devices)} VTYsh device connection tests passed")

    @aetest.subsection
    def test_bash_connections(self):
        """Test connecting to all devices using bash connection"""
        global global_testbed
        
        logger.info(banner("Testing Bash connections"))
        
        # Verify testbed is available
        assert global_testbed is not None, "Testbed not loaded"
        
        connection_results = []
        
        for device_name, device in global_testbed.devices.items():
            logger.info(f"Testing Bash connection to {device_name}")
            
            try:
                # 1. Connect to the device using bash connection with alias
                logger.info(f"  Connecting to {device_name} with Bash...")
                device.connect(via='bash', alias='bash_conn')
                
                # 2. Verify connection is established
                if device.bash_conn.connected:
                    logger.info(f"  ✓ Successfully connected to {device_name} via Bash")
                else:
                    raise Exception(f"Bash connection failed to {device_name}")
                
                # 3. Test bash command execution
                logger.info(f"  Testing Bash command execution...")
                try:
                    # Execute basic bash commands to verify device responsiveness
                    output = device.bash_conn.execute('whoami')
                    logger.info(f"  ✓ Bash command execution successful on {device_name}")
                    logger.info(f"  Current user: {output.strip()}")
                    
                    # Test another bash command
                    hostname_output = device.bash_conn.execute('hostname')
                    logger.info(f"  Device hostname: {hostname_output.strip()}")
                    
                except Exception as cmd_error:
                    logger.warning(f"  ⚠ Bash command execution failed on {device_name}: {cmd_error}")
                    # Don't fail the test for command issues, just log it
                
                # 4. Disconnect from the device
                logger.info(f"  Disconnecting from {device_name}...")
                device.bash_conn.disconnect()
                
                # 5. Verify connection is properly closed
                if not device.bash_conn.connected:
                    logger.info(f"  ✓ Successfully disconnected from {device_name}")
                    connection_results.append((device_name, True, "Bash Success"))
                else:
                    raise Exception(f"Bash disconnect failed for {device_name}")
                    
            except Exception as e:
                logger.error(f"  ✗ Bash connection test failed for {device_name}: {str(e)}")
                connection_results.append((device_name, False, str(e)))
        
        # Evaluate overall results
        failed_devices = [name for name, success, msg in connection_results if not success]
        successful_devices = [name for name, success, msg in connection_results if success]
        
        logger.info(f"Bash connection test summary:")
        logger.info(f"  ✓ Successful: {len(successful_devices)} devices: {', '.join(successful_devices)}")
        if failed_devices:
            logger.error(f"  ✗ Failed: {len(failed_devices)} devices: {', '.join(failed_devices)}")
        
        if failed_devices:
            self.failed(f"Bash connection tests failed for {len(failed_devices)} devices: {', '.join(failed_devices)}")
        else:
            self.passed(f"All {len(successful_devices)} Bash device connection tests passed")

class SonicBashPingTest(aetest.Testcase):
    """Test cases for SONiC network ping using bash only"""
    
    @aetest.setup
    def setup(self):
        """Setup for bash ping tests"""
        global global_testbed
        self.testbed = global_testbed
        assert self.testbed is not None, "Global testbed not available"
        
    @aetest.test
    def test_bash_ping_connectivity(self):
        """Test network connectivity using bash ping commands only"""
        logger.info(banner("Testing network connectivity using Bash ping"))
        
        # Define data interface connectivity map based on docker-compose networks
        data_links = [
            # Direct neighbor connectivity tests
            ('sonic-1', '192.1.2.11', 'sonic-2', '192.1.2.12'),  # link_1_2
            ('sonic-2', '192.2.3.12', 'sonic-3', '192.2.3.13'),  # link_2_3
            ('sonic-3', '192.3.4.13', 'sonic-4', '192.3.4.14'),  # link_3_4
            ('sonic-1', '192.1.5.11', 'sonic-5', '192.1.5.15'),  # link_1_5
            ('sonic-5', '192.5.6.15', 'sonic-6', '192.5.6.16'),  # link_5_6
            ('sonic-6', '192.4.6.16', 'sonic-4', '192.4.6.14'),  # link_6_4
        ]
        
        ping_test_passed = True
        
        for src_device, src_ip, dst_device, dst_ip in data_links:
            logger.info(f"Testing bash ping: {src_device} ({src_ip}) -> {dst_device} ({dst_ip})")
            
            try:
                # Get source device object
                source_device = self.testbed.devices[src_device]
                
                # Connect to source device using bash connection with alias
                if not hasattr(source_device, 'bash_conn') or not source_device.bash_conn.connected:
                    logger.info(f"  Connecting to {src_device} via bash...")
                    source_device.connect(via='bash', alias='bash_conn')
                
                # Execute ping command using bash connection
                ping_command = f"ping -c 3 -W 2 {dst_ip}"
                logger.info(f"  Executing bash command: {ping_command}")
                
                try:
                    ping_output = source_device.bash_conn.execute(ping_command, timeout=10)
                    
                    # Check if ping was successful (look for "3 received" or "0% packet loss")
                    if "3 received" in ping_output or "0% packet loss" in ping_output:
                        logger.info(f"  ✓ Bash ping successful: {src_device} -> {dst_device}")
                    else:
                        logger.error(f"  ✗ Bash ping failed: {src_device} -> {dst_device}")
                        logger.error(f"  Ping output: {ping_output}")
                        ping_test_passed = False
                        
                except Exception as ping_error:
                    logger.error(f"  ✗ Bash ping command failed: {src_device} -> {dst_device}: {ping_error}")
                    ping_test_passed = False
                
                # Test bidirectional connectivity (reverse direction)
                logger.info(f"Testing reverse bash ping: {dst_device} ({dst_ip}) -> {src_device} ({src_ip})")
                
                try:
                    # Get destination device object
                    dest_device = self.testbed.devices[dst_device]
                    
                    # Connect to destination device using bash connection with alias
                    if not hasattr(dest_device, 'bash_conn') or not dest_device.bash_conn.connected:
                        logger.info(f"  Connecting to {dst_device} via bash...")
                        dest_device.connect(via='bash', alias='bash_conn')
                    
                    # Execute reverse ping command using bash connection
                    reverse_ping_command = f"ping -c 3 -W 2 {src_ip}"
                    logger.info(f"  Executing bash command: {reverse_ping_command}")
                    
                    reverse_ping_output = dest_device.bash_conn.execute(reverse_ping_command, timeout=10)
                    
                    # Check if reverse ping was successful
                    if "3 received" in reverse_ping_output or "0% packet loss" in reverse_ping_output:
                        logger.info(f"  ✓ Reverse bash ping successful: {dst_device} -> {src_device}")
                    else:
                        logger.error(f"  ✗ Reverse bash ping failed: {dst_device} -> {src_device}")
                        logger.error(f"  Reverse ping output: {reverse_ping_output}")
                        ping_test_passed = False
                        
                except Exception as reverse_ping_error:
                    logger.error(f"  ✗ Reverse bash ping command failed: {dst_device} -> {src_device}: {reverse_ping_error}")
                    ping_test_passed = False
                    
            except Exception as e:
                logger.error(f"  ✗ Failed to test bash connectivity {src_device} <-> {dst_device}: {str(e)}")
                ping_test_passed = False
        
        if ping_test_passed:
            self.passed("Bash ping testing completed successfully")
        else:
            self.failed("Some bash ping tests failed")
        
        # Cleanup: Disconnect all devices
        logger.info("Cleaning up bash connection devices...")
        for device_name, device in self.testbed.devices.items():
            try:
                if hasattr(device, 'bash_conn') and device.bash_conn.connected:
                    device.bash_conn.disconnect()
                    logger.info(f"  Disconnected bash connection from {device_name}")
            except Exception as e:
                logger.warning(f"  Failed to disconnect bash connection from {device_name}: {e}")

class CommonCleanup(aetest.CommonCleanup):
    """Common cleanup tasks"""
    
    @aetest.subsection
    def cleanup(self):
        """Cleanup after all tests"""
        logger.info(banner("Cleaning up test environment"))
        # Add any cleanup tasks here

if __name__ == '__main__':
    # Run the test
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='SONiC Network Test Script')
    parser.add_argument('--testbed', '-t', 
                       help='Path to testbed YAML file',
                       default='testbed.yaml')
    
    args = parser.parse_args()
    
    # For standalone execution without testbed file
    if len(sys.argv) == 1:
        logger.info("Running basic test without testbed file")
        aetest.main()
    else:
        # Load testbed object from YAML file
        logger.info(f"Loading testbed from: {args.testbed}")
        testbed_obj = loader.load(args.testbed)
        logger.info(f"Testbed loaded with {len(testbed_obj.devices)} devices")
        
        # Run with testbed object
        aetest.main(testbed=testbed_obj)
