#!/bin/bash
# FRR and SSH startup script for SONiC

echo "Configuring FRR and SSH..."

# Copy FRR configuration files to proper location
if [ -f /etc/sonic/daemons ]; then
    cp /etc/sonic/daemons /etc/frr/daemons
    chown frr:frr /etc/frr/daemons
    chmod 640 /etc/frr/daemons
    echo "FRR daemons configuration updated"
fi

# Set up SSH users and configuration
echo "Setting up SSH..."

# Create admin user if it doesn't exist
if ! id "admin" &>/dev/null; then
    useradd -m -s /bin/bash -G sudo admin
    echo "Created admin user"
fi

# Set passwords
echo "admin:admin" | chpasswd
echo "root:admin" | chpasswd

# Configure SSH
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# Start SSH service
service ssh start
echo "SSH service started"

# Start FRR services
echo "Starting FRR services..."
supervisorctl start bgpd
echo "BGP daemon started"

echo "FRR and SSH configuration complete"
