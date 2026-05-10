# Basic Ubuntu 22.04 image
FROM ubuntu:22.04

# common practice
RUN apt-get update

# set shell to bash, set -c flag so the commands are interpreted as strings by deafult
SHELL ["/bin/bash", "-c"]

# set informative colors for the building process
ENV BUILDKIT_COLORS=run=green:warning=yellow:error=red:cancel=cyan

# start with root user
USER root

# build-time argument given by build_docker.sh
ARG HOST_USER_GROUP_ARG
ARG USE_VSCODE

# create group appuser with id 999
# create grour hostgroup. This is needed so appuser can manipulate the host file without sudo
# create user appuser: home at /home/appuser, default shell is bash, id 999 and add to appuser group  
# set sudo password as admin for user appuser
# add user appuser to the following groups:
#   sudo (admin privis)
#   hostgroup
#   adm (system logging) --> might not be necessary
#   dip (network devices)
# finally, copy a .bashrc file into the container
RUN groupadd -g 999 appuser && \
    groupadd -g $HOST_USER_GROUP_ARG hostgroup && \
    useradd --create-home --shell /bin/bash -u 999 -g appuser appuser && \
    echo 'appuser:admin' | chpasswd && \
    usermod -aG sudo,hostgroup,adm,dip appuser && \
    cp /etc/skel/.bashrc /home/appuser/

# set working directory
WORKDIR /home/appuser

ENV DEBIAN_FRONTEND=noninteractive

# Install system packages + Python
RUN apt-get update && \
    apt-get install -y \
    software-properties-common \
    git \
    build-essential \
    wget \
    curl \
    jq \
    gdb \
    sudo \
    nano \
    net-tools \
    unzip \
    libgl1 \
    cmake \
    python3 \
    python3-pip \
    python3-venv \
    # Playwright dependencies
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    fonts-liberation \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY misc/requirements.txt /tmp/requirements.txt

# Install Python requirements
RUN python3 -m pip install --upgrade pip && \
    pip3 install -r /tmp/requirements.txt

# Start as appuser
USER appuser

# Install Playwright browsers
RUN python3 -m playwright install chromium