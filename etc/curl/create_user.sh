#!/usr/bin/env bash

HOST='localhost:5000'

# -H "Authorization: Bearer $(pass 'api-keys/deepseek')" \

curl -X POST http://$HOST/api/users/user \
    -H "Content-Type: application/json" \
    -d '{
        "username": "shepard",
        "email": "shepard@mass-effect.com",
	"password": "password12345678"
      }'
