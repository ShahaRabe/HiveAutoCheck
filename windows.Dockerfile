FROM mcr.microsoft.com/windows-cssc/python:3.11-windows-ltsc2019

RUN mkdir /mnt/autocheck

# Set PowerShell as the default shell
SHELL ["powershell", "-Command"]

# Install Chocolatey (for package management)
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; \
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; \
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1')); \
    refreshenv

# Install Python, 7-Zip, UnRAR, CMake, Make, Clang, GCC, G++, and MSVC using Chocolatey
RUN choco install -y 7zip \
    unrar \
    cmake \
    make \
    llvm \
    mingw \
    visualstudio2022buildtools --package-parameters "--includeRecommended --passive --wait"

# Refresh environment variables
RUN refreshenv

# Verify installations
RUN python --version
RUN 7z
RUN unrar
RUN cmake --version
RUN make --version
RUN clang --version
RUN gcc --version
RUN g++ --version

RUN mkdir /tmp
COPY autocheck/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY ./dist/*.whl /tmp/
RUN python3 -m pip install /tmp/*.whl

COPY autocheck /test
WORKDIR /

ENTRYPOINT python3 -m test