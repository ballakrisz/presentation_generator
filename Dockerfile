FROM ubuntu:22.04

SHELL ["/bin/bash", "-c"]

ENV DEBIAN_FRONTEND=noninteractive
ENV BUILDKIT_COLORS=run=green:warning=yellow:error=red:cancel=cyan

ARG HOST_USER_GROUP_ARG
ARG USE_VSCODE

# --------------------------------------------------
# SYSTEM + OCR + PDF + OPENCV + PLAYWRIGHT
# --------------------------------------------------

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # basic
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
    cmake \
    # python
    python3 \
    python3-pip \
    python3-venv \
    # PDF processing
    poppler-utils \
    # OCR
    tesseract-ocr \
    # OpenCV runtime deps
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    # Playwright / Chromium
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
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------
# USER SETUP
# --------------------------------------------------

RUN groupadd -g 999 appuser && \
    groupadd -g ${HOST_USER_GROUP_ARG} hostgroup && \
    useradd \
        --create-home \
        --shell /bin/bash \
        -u 999 \
        -g appuser \
        appuser && \
    echo 'appuser:admin' | chpasswd && \
    usermod -aG sudo,hostgroup,adm,dip appuser && \
    cp /etc/skel/.bashrc /home/appuser/.bashrc && \
    chown appuser:appuser /home/appuser/.bashrc

WORKDIR /home/appuser

# --------------------------------------------------
# PYTHON REQUIREMENTS
# --------------------------------------------------

COPY misc/requirements.txt /tmp/requirements.txt

RUN python3 -m pip install --upgrade pip && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt

# --------------------------------------------------
# PLAYWRIGHT
# --------------------------------------------------

USER appuser

RUN python3 -m playwright install chromium