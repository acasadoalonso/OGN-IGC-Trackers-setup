UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)

all: TRKsetup VALI-AVX vali-avx vali-avx.o

TRKsetup: 	TRKsetup.py
		cd /nfs/OGN/src/TRKSsrc
		rm -rf build/*
		@echo " "
		@echo "==================== gen TRKsetup ==================="
		@echo " "
		pyinstaller -F --noconfirm --clean --key OGNOGNOGNOGNOGN --name TRKsetup.$(UNAME_S)$(UNAME_M) TRKsetup.py
		rm -rf build/* 

VALI-AVX: 	VALI-AVX.py
		cd /nfs/OGN/src/TRKSsrc
		rm -rf build/* 
		@echo " "
		@echo "==================== gen VALI-AVX ==================="
		@echo " "
		pyinstaller -F --noconfirm --clean --key OGNOGNOGNOGNOGN --name VALI-AVX.$(UNAME_S)$(UNAME_M) VALI-AVX.py
		rm -rf build/* 
vali-avx: 	vali-avx.cc *.h
		cd /nfs/OGN/src/TRKSsrc
		g++ -Wall -O2 -o dist/vali-avx.$(UNAME_S)$(UNAME_M).exe vali-avx.cc -lmbedcrypto -lmbedx509 -lmbedtls
vali-avx.o:   	vali-avx.cc *.h
		cd /nfs/OGN/src/TRKSsrc
		x86_64-w64-mingw32-g++-win32 -Wall -Wno-misleading-indentation -O2 -Imbedtls/include -lmbedtls/visualc/VS2010/x64/Release/mbedTLS.lib -static -c -o dist/vali-avx.o vali-avx.cc 

clean:		cleanlocal cleanfai

cleanlocal:
		rm -rf dist/TRKsetup* dist/VALI* dist/TRKtools* dist/vali* *.spec build/ dist/build/
cleanfai:
		ansible-playbook distclean.yml

