UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)
TRACKERSRC := ../esp32-ogn-tracker
SRC := /nfs/OGN/src/TRKSsrc


all: TRKsetup VALI-AVX vali-avx vali-avx.o

TRKsetup: 	TRKsetup.py
		cd $(SRC) && rm -rf build/*
		@echo " "
		@echo "==================== gen TRKsetup ==================="
		@echo " "
		pyinstaller -F --noconfirm --clean --key OGNOGNOGNOGNOGN --name TRKsetup.$(UNAME_S)$(UNAME_M) TRKsetup.py
		cd $(SRC) && rm -rf build/* 

VALI-AVX: 	VALI-AVX.py
		cd $(SRC) && rm -rf build/* 
		@echo " "
		@echo "==================== gen VALI-AVX ==================="
		@echo " "
		pyinstaller -F --noconfirm --clean --key OGNOGNOGNOGNOGN --name VALI-AVX.$(UNAME_S)$(UNAME_M) VALI-AVX.py
		cd $(SRC) && rm -rf build/* 

vali-avx: 	vali-avx.cc *.h
		g++ -Wall -O2 -o dist/vali-avx.$(UNAME_S)$(UNAME_M).exe vali-avx.cc -lmbedcrypto -lmbedx509 -lmbedtls

vali-avx.o:   	vali-avx.cc *.h
		x86_64-w64-mingw32-g++-win32 -Wall -Wno-misleading-indentation -O2 -Imbedtls/include -lmbedtls/visualc/VS2010/x64/Release/mbedTLS.lib -static -c -o dist/vali-avx.o vali-avx.cc 

tarbal:		dist/TRKtools.tgz	

dist/TRKtools.tgz: *.py *.cc *.h 		
		@echo "==============================================================="
		@echo ">>> create the tarball TRKTOOLS.tgz <<<"
		@echo "==============================================================="
		tar cvzf TRKtools.tgz --exclude='*tgz' dist/*
		mv       TRKtools.tgz dist
		@echo "========================"

firmware:	dist/esp32-ogn-tracker-bin.tgz

dist/esp32-ogn-tracker-bin.tgz:	$(TRACKERSRC)/build/esp32-ogn-tracker.elf
		@echo "==============================================================="
		@echo "   Get a copy of the firmware into the distribution directory  "
		@echo "   ----------------------------------------------------------  "
		cd $(TRACKERSRC) && pwd && bash bin-arch.sh && mv *tgz ../TRKSsrc/dist/
		@echo "==============================================================="
		

clean:		cleanlocal cleanfai

cleanlocal:
		rm -rf dist/TRKsetup* dist/VALI* dist/TRKtools* dist/vali* *.spec build/ dist/build/ dist/*.tgz dist/*template dist/README.md
cleanfai:
		ansible-playbook distclean.yml

