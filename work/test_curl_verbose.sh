#!/bin/bash
curl -v -X POST http://localhost:8191/v1 \
  -H 'Content-Type: application/json' \
  -d '{"cmd":"sessions.list"}' 2>&1 | grep -E '(^> |^< |HTTP)'
