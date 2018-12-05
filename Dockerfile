FROM base/archlinux

RUN pacman -Suy && \
    pacman -S --noconfirm python3 python-pip base-devel && \
    pip install pycrypto numpy

WORKDIR "/code"
