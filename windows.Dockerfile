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
    visualstudio2022buildtools --version=17.4.0 --package-parameters "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --includeOptional --passive --wait"

ENV VSINSTALLDIR="C:\\Program Files\\Microsoft Visual Studio\\2022\\BuildTools"
ENV VisualStudioDir="C:\\Program Files\\Microsoft Visual Studio\\2022\\BuildTools"
ENV Path="${VSINSTALLDIR}\\MSVC\\14.30.30705\\bin\\Hostx64\\x64;${Path}"

RUN mkdir /tmp
COPY autocheck/requirements.txt /tmp/requirements.txt
RUN python -m pip install -r /tmp/requirements.txt

COPY ./dist/*.whl /tmp/
RUN python -m pip install /tmp/hive_autocheck-0.1.0-py3-none-any.whl

COPY autocheck /test
WORKDIR /

ENTRYPOINT python -m test
