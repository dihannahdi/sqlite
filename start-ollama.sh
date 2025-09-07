#!/bin/bash

# Start Ollama server in background
echo "Starting Ollama server..."
ollama serve &

# Wait for Ollama to start
echo "Waiting for Ollama to start..."
sleep 10

# Pull SmolLM2-360M-Instruct model
echo "Pulling SmolLM2-360M-Instruct model..."
ollama pull SmolLM2-360M-Instruct

echo "SmolLM2 model ready!"

# Keep container running
wait
