apt install -y --no-install-recommends automake autoconf build-essential git
apt install -y --no-install-recommends libtool libxext-dev libx11-dev x11proto-gl-dev
apt install -y --no-install-recommends x11proto-dev xvfb libgl1 libglvnd-dev libegl1 pkg-config

apt update
apt install -y --no-install-recommends --fix-missing \
    automake \
    autoconf \
    build-essential \
    git \
    libbz2-dev \
    libegl1 \
    libfontconfig1 \
    libgl1 \
    libglvnd-dev \
    libgtk-3-0 \
    libsm6 \
    libtool \
    libx11-6 \
    libx11-dev \
    libxcursor1 \
    libxext6 \
    libxext-dev \
    libxi6 \
    libxinerama1 \
    libxkbcommon0 \
    libxrandr2 \
    libxrender1 \
    libxxf86vm1 \
    mesa-utils \
    pkg-config \
    wget

apt install -y gdb

# Clone and build libglvnd for NVIDIA EGL support
git clone https://github.com/NVIDIA/libglvnd.git /tmp/libglvnd \
    && cd /tmp/libglvnd \
    && ./autogen.sh \
    && ./configure \
    && make -j$(nproc) \
    && make install \
    && mkdir -p /usr/share/glvnd/egl_vendor.d/ \
    && printf "{\n\
    \"file_format_version\" : \"1.0.0\",\n\
    \"ICD\": {\n\
        \"library_path\": \"libEGL_nvidia.so.0\"\n\
    }\n\
    }" > /usr/share/glvnd/egl_vendor.d/10_nvidia.json \
    && cd / \
    && rm -rf /tmp/libglvnd
