#!/bin/bash
# Configure passwordless sudo for all commands

echo "Configuring passwordless sudo for user: tishko"

# Create sudoers file for all commands
echo 'tishko' | sudo -S bash -c "echo 'tishko ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/tishko"
sudo chmod 0440 /etc/sudoers.d/tishko

# Verify
if sudo -n true 2>/dev/null; then
    echo "✅ Passwordless sudo configured successfully!"
    echo "You can now run any sudo command without a password."
else
    echo "❌ Configuration failed"
    exit 1
fi
