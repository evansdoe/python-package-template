ARG VENV_PATH="/opt/venv"
ARG PYTHON_VERSION={{ cookiecutter.python_version }}

{%- if cookiecutter.include_gpu %}
## GPU: use NVIDIA CUDA base image
## The cuda version specified here must match the one in `.devcontainer/docker-compose.yml`
ARG FROM_IMAGE=nvidia/cuda:12.4.1-runtime-ubuntu22.04
{%- else %}
## CPU-only: use Debian slim
ARG FROM_IMAGE=debian:stable-slim
{%- endif %}

ARG FROM_IMAGE_RUNTIME=${FROM_IMAGE}
ARG FROM_IMAGE_DEV=build

ARG DEBIAN_FRONTEND=noninteractive

# ==============================================================================
# Build Stage
# ==============================================================================
FROM $FROM_IMAGE AS build
ARG VENV_PATH
ARG DEBIAN_FRONTEND
ARG PYTHON_VERSION

LABEL maintainer="{{ cookiecutter.author_name }} <{{ cookiecutter.author_email }}>"

# Required for packages with native extensions (for example `lzf`).
RUN apt-get update && apt-get install -yq \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# THIS WILL BREAK REPRODUCIBILITY, AND MIGHT CAUSE TROUBLES DURING RUNTIME!
# AFTER YOU THOUGHT TWICE ABOUT IT, YOU MIGHT WANT TO CONSIDER PINNING VERSIONS AT LEAST ;)
# system dependencies, these are necessary to run your software
# RUN apt-get update && apt-get install -yq \
    # ca-certificates=1.18.0 \
    # && apt-get clean && rm -rf /var/lib/apt/lists/*

# uv version: latest
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# # uv version: pinned
# COPY --from=ghcr.io/astral-sh/uv:{{ cookiecutter.uv_version }} /uv /uvx /bin/

# Setup directory structure
# https://github.com/GoogleContainerTools/kaniko/issues/1508
RUN rm -rf /workspace

# prepare workspace and dependencies
WORKDIR /workspace
COPY pyproject.toml *.lock README* ./

# ensure Python uses this virtual environment
ENV VIRTUAL_ENV=$VENV_PATH \
    UV_PROJECT_ENVIRONMENT=${VENV_PATH} \
    PATH="$VENV_PATH/bin:$PATH" \
    UV_HTTP_TIMEOUT=300
RUN uv venv --python $PYTHON_VERSION && uv sync && uv cache prune --ci

# ==============================================================================
# Runtime Stage
# ==============================================================================
# TODO: build from FROM_IMAGE (or a plain python img), and just copy from build (without pyenv, uv)
FROM $FROM_IMAGE_RUNTIME AS runtime
ARG VENV_PATH
ARG DEBIAN_FRONTEND

# prepare workspace and dependencies
WORKDIR /workspace

# copy the virtual environment from the build stage - careful this won't work with the current setup
# see: https://github.com/astral-sh/uv/issues/6782
COPY --from=build $VENV_PATH $VENV_PATH

# Copy the rest of the repository
COPY . .

CMD ["bash"]

# ==============================================================================
# Development Stage
# ==============================================================================
FROM $FROM_IMAGE_DEV AS dev
ARG VENV_PATH
ARG DEBIAN_FRONTEND

RUN apt-get update && apt-get install -yq \
    git \
    tmux \
    zsh \
    htop \
    glances \
    tree \
    curl \
    neovim \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# install development dependencies
RUN uv sync --all-extras --all-groups && uv cache prune --ci

# Set timezone
ARG TZ={{ cookiecutter.timezone }}
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install tmux, vim and oh-my-zsh
RUN set -ex \
    && cd \
    && git clone https://github.com/gpakosz/.tmux.git \
    && ln -s -f .tmux/.tmux.conf && cp .tmux/.tmux.conf.local . \
    && curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh | bash
ENV SHELL=/bin/zsh
CMD ["zsh"]
