#!/bin/bash
set -e

echo "Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
sleep 5

echo "Pulling Qwen2.5-1.5B model..."
# Try multiple model names for compatibility
if ! ollama pull qwen2.5:1.5b; then
    echo "Primary qwen2.5:1.5b failed, trying alternative name..."
    if ! ollama pull qwen2.5:1.5b-instruct; then
        echo "Alternative failed, trying qwen2.5:0.5b as lightweight fallback..."
        if ! ollama pull qwen2.5:0.5b; then
            echo "Fallback failed, trying tinyllama as emergency fallback..."
            ollama pull tinyllama || {
                echo "All model pulls failed! Check Ollama service status."
                exit 1
            }
        fi
    fi
fi

echo "Model successfully loaded!"

# Keep the script running to prevent container exit
wait $OLLAMA_PID