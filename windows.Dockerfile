FROM mcr.microsoft.com/windows-cssc/python:3.11-servercore-ltsc2022 as vs_installer

# Restore the default Windows shell for correct batch processing.
SHELL ["cmd", "/S", "/C"]
RUN mkdir C:\tmp

RUN \
    # Download the Build Tools bootstrapper.
    curl -SL --output C:\tmp\vs_buildtools.exe https://aka.ms/vs/17/release/vs_buildtools.exe \
    \
    # Install Build Tools with the Microsoft.VisualStudio.Workload.VCTools workload, excluding workloads and components with known issues.
    && (start /w C:\tmp\vs_buildtools.exe --quiet --wait --norestart --nocache \
        --installPath "%ProgramFiles%\Microsoft Visual Studio\2022\BuildTools" \
        --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended \
        --remove Microsoft.VisualStudio.Component.Windows10SDK.10240 \
        --remove Microsoft.VisualStudio.Component.Windows10SDK.10586 \
        --remove Microsoft.VisualStudio.Component.Windows10SDK.14393 \
        --remove Microsoft.VisualStudio.Component.Windows81SDK \
        || IF "%ERRORLEVEL%"=="3010" EXIT 0)

FROM mcr.microsoft.com/windows-cssc/python:3.11-servercore-ltsc2022 as builder

RUN (mkdir "C:\Program Files\Microsoft Visual Studio\2022" || IF "%ERRORLEVEL%"=="1" EXIT 0)
COPY --from=vs_installer "C:\Program Files\Microsoft Visual Studio\2022\BuildTools" "C:\Program Files\Microsoft Visual Studio\2022\BuildTools"
COPY --from=vs_installer "C:\Program Files (x86)\Windows Kits" "C:\Program Files (x86)\Windows Kits"
COPY --from=vs_installer "C:\Program Files" "C:\Program Files"
COPY --from=vs_installer "C:\Program Files (x86)" "C:\Program Files (x86)"
RUN setx Path "%Path%;%ProgramFiles%\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin"

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
    mingw

RUN mkdir /mnt/autocheck
RUN mkdir /tmp
COPY autocheck/requirements.txt /tmp/requirements.txt
RUN python -m pip install -r /tmp/requirements.txt

COPY ./dist/*.whl /tmp/
RUN python -m pip install /tmp/hive_autocheck-0.1.0-py3-none-any.whl

COPY autocheck /test
WORKDIR /


ENTRYPOINT python -m test
