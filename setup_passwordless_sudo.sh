#!/bin/bash
# Setup passwordless sudo for mount operations

echo "Setting up passwordless sudo for mount/umount..."
echo 'tishko' | sudo -S tee /etc/sudoers.d/mount-z > /dev/null << 'EOF'
tishko ALL=(ALL) NOPASSWD: /bin/mount, /bin/umount, /usr/bin/mkdir
EOF

echo 'tishko' | sudo -S chmod 0440 /etc/sudoers.d/mount-z

echo "✅ Passwordless sudo configured successfully"
echo "Testing mount..."
sudo umount /mnt/z 2>/dev/null
sudo mkdir -p /mnt/z
sudo mount -t drvfs 'Z:' /mnt/z -o metadata,uid=1000,gid=1000

if [ $? -eq 0 ]; then
    echo "✅ Z: drive mounted successfully without password!"
else
    echo "❌ Mount failed"
fi
