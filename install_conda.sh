#!/bin/bash

install_miniconda() {
    echo "Miniconda no está instalado. Procediendo a instalarlo..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh -O Miniconda3-latest-Linux-aarch64.sh
    bash Miniconda3-latest-Linux-aarch64.sh -b -p $HOME/miniconda
    rm Miniconda3-latest-Linux-aarch64.sh
    export PATH="$HOME/miniconda/bin:$PATH"
    echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
}

install_miniconda