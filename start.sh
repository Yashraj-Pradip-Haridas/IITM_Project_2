#!/bin/bash

# Use the PORT assigned by Render, or default to 8000 if not set
PORT=${PORT:-8000}

#!/bin/bash
uvicorn main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips '*'

