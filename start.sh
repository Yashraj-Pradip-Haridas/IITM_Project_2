#!/bin/bash

# Use the PORT assigned by Render, or default to 8000 if not set
PORT=${PORT:-8000}

uvicorn main:app --host 0.0.0.0 --port $PORT
