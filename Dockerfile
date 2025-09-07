# Dockerfile for Ollama SmolLM2 Service on Railway
FROM ollama/ollama:latest

# Set environment variables
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_KEEP_ALIVE=-1

# Expose port
EXPOSE 11434

# Copy startup script
COPY start-ollama.sh /start-ollama.sh
RUN chmod +x /start-ollama.sh

# Start Ollama with SmolLM2 model
CMD ["/start-ollama.sh"]
