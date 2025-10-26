#!/bin/bash
# Run from pure bash environment

cd /mnt/c/tesseract/work

echo "Running curl directly from bash:"
curl -s -X POST http://localhost:8191/v1 -H 'Content-Type: application/json' -d '{"cmd":"sessions.list"}' | head -c 100
echo ""

echo -e "\nRunning same via Python subprocess:"
python3 << 'EOF'
import subprocess
cmd = "curl -s -X POST http://localhost:8191/v1 -H 'Content-Type: application/json' -d '{\"cmd\":\"sessions.list\"}'"
result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
print(f"Return code: {result.returncode}")
if result.stdout:
    print(f"Output: {result.stdout[:100]}")
EOF
