#!/bin/bash
# Configure passwordless sudo for mounting Z: drive

echo "Configuring passwordless sudo for mount operations..."

# Create sudoers file for mount/umount
echo 'tishko ALL=(ALL) NOPASSWD: /bin/mount, /bin/umount' | sudo tee /etc/sudoers.d/mount-z > /dev/null
sudo chmod 0440 /etc/sudoers.d/mount-z

# Ensure mount point exists
sudo mkdir -p /mnt/z

# Test the configuration
echo "Testing passwordless mount..."
sudo umount /mnt/z 2>/dev/null || true
sudo mount -t drvfs 'Z:' /mnt/z -o metadata,uid=1000,gid=1000

if [ $? -eq 0 ]; then
    echo "✅ Z: drive mounted successfully without password!"
    
    # Create all required directories for training
    mkdir -p /mnt/z/training_output_best/{logs,tmp,ground_truth,model}
    
    echo "✅ All directories created:"
    ls -la /mnt/z/training_output_best/ | head -10
else
    echo "❌ Mount failed"
    exit 1
fi
