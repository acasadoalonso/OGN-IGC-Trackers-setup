#!/bin/bash
pip install --upgrade pip			
pip -V								
pip install ephem pytz geopy configparser 	
pip install pycountry			
pip install beeprint ogn.client		
pip install tqdm psutil 			
pip install ttn pyserial serial				
pip install eciespy pycryptodome             
pip install python_cayennelpp
pip install --upgrade google-api-python-client
pip install tinyaes
pip install --upgrade python-mbedtls
pip install pyinstaller pyreqs
python --version
# On Developper PowerShell for VS 2022
# ====================================
git clone https://github.com/ARMmbed/mbedtls.git 
cd mbedtls
git switch mbedtls-2.16
$env:MBEDTLSROOT= $(pwd)
MSBuild.exe /NoLogo /MaxCpuCount /p:Configuration=Release /p:Platform=x64 /p:PlatformToolset=v143 /p:WholeProgramOptimization=False .\visualc\VS2010\mbedTLS.sln 
$env:include += ";$(pwd)\include"
$env:LIB = "$(pwd)\visualc\VS2010\x64\Release"
export MBEDTLSROOT=$(pwd)
export include="$include;$(pwd)\include"
export LIB="$(pwd)\visualc\VS2010\x64\Release"
cd ..
git clone https://github.com/Synss/python-mbedtls.git
cd python-mbedtls
# on Git Bash
# ===========
python setup.py install

