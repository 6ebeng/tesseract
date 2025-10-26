#!/bin/bash
# Test FlareSolverr API

echo "Testing FlareSolverr POST API..."

# Test 1: List sessions
echo -e "\n1. List sessions:"
curl -s -X POST http://localhost:8191/v1 \
  -H 'Content-Type: application/json' \
  -d '{"cmd":"sessions.list"}' | python3 -m json.tool

# Test 2: Create session
echo -e "\n2. Create session:"
curl -s -X POST http://localhost:8191/v1 \
  -H 'Content-Type: application/json' \
  -d '{"cmd":"sessions.create","session":"test_session_bash"}' | python3 -m json.tool
