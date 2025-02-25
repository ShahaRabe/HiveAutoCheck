FROM mcr.microsoft.com/windows-cssc/python:3.11-server-ltsc2022

RUN mkdir /mnt/autocheck

# Set PowerShell as the default shell
SHELL ["powershell", "-Command"]

# Install Chocolatey (for package management)
RUN Set-ExecutionPolicy Bypass -Scope Process -Force; \
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; \
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'));

# Install Python, 7-Zip, UnRAR, CMake, Make, Clang, GCC, G++, and MSVC using Chocolatey
RUN choco install -y 7zip \
    cmake \
    make \
    llvm \
    mingw \
    visualstudio2022buildtools --package-parameters "--includeRecommended --passive --wait"

RUN mkdir /tmp
COPY autocheck/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY ./dist/*.whl /tmp/
RUN python3 -m pip install /tmp/*.whl

COPY autocheck /test
WORKDIR /

ENTRYPOINT python3 -m test
