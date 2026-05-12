FROM python:3.13-slim

# Install uv from the official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user
# Switch to the "user" user
USER user

# Set home to the user's home directory and add it to PATH
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Enable bytecode compilation and fix virtual environment path
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Expose the necessary ports for FastAPI and Gradio
EXPOSE 7860

# Copy dependency files with appropriate ownership
COPY --chown=user pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy the rest of the application setting the ownership
COPY --chown=user . .

# Start both applications using the entrypoint script
CMD ["uv", "run", "python", "app.py"]
