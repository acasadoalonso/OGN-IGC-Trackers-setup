UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)
TRACKERSRC := ../esp32-ogn-tracker
SRC := /nfs/OGN/src/TRKSsrc


all: TRKsetup VALI-AVX vali-avx dist/vali-avx.obj

TRKsetup:	dist/TRKsetup.$(UNAME_S)$(UNAME_M)

dist/TRKsetup.$(UNAME_S)$(UNAME_M): 	TRKsetup.py config.py netparams.py

		cd $(SRC)      && rm -rf build/*
		cd $(SRC)/dist && rm -rf build/*
		@echo " "
		@echo "==================== gen TRKsetup ==================="
		@echo " "
		pyinstaller -F --noconfirm --clean --key OGNOGNOGNOGNOGN --name TRKsetup.$(UNAME_S)$(UNAME_M) TRKsetup.py
		cd $(SRC) && rm -rf build/* 

VALI-AVX: 	dist/VALI-AVX.$(UNAME_S)$(UNAME_M) 

dist/VALI-AVX.$(UNAME_S)$(UNAME_M): 	VALI-AVX.py config.py netparams.py
		cd $(SRC)      && rm -rf build/* 
		cd $(SRC)/dist && rm -rf build/* 
		@echo " "
		@echo "==================== gen VALI-AVX ==================="
		@echo " "
		pyinstaller -F --noconfirm --clean --key OGNOGNOGNOGNOGN --name VALI-AVX.$(UNAME_S)$(UNAME_M) VALI-AVX.py
		cd $(SRC) && rm -rf build/* 

vali-avx:	vali-avx.cc *.h
		g++ -Wall -O2 vali-avx.cc   -lmbedcrypto -lmbedx509 -lmbedtls -o dist/vali-avx.$(UNAME_S)$(UNAME_M).exe
		touch dist/vali-avx.$(UNAME_S)$(UNAME_M).exe

dist/vali-avx.obj:  	vali-avx.cc *.h
		x86_64-w64-mingw32-g++-win32 -Wall -Wno-misleading-indentation -O2 -Imbedtls/include -lmbedtls/visualc/VS2010/x64/Release/mbedTLS.lib -static -c -o dist/vali-avx.obj vali-avx.cc 
		touch dist/vali-avx.obj

tarbal:		dist/TRKtools.tgz	docs/OGN-Tracking-WGC.pdf

dist/TRKtools.tgz: *.py *.cc *.h dist/vali*
		

		cd $(SRC) && rm -rf build/*
		rm -f *.spec 
		rm -f dist/TRK*.tgz
		rm -f dist/TRK*.zip
		@echo "==============================================================="
		@echo ">>>         create the tarball TRKTOOLS.tgz/.zip <<<           "
		@echo "==============================================================="
		tar cvzf TRKtools.tgz --exclude='*.tgz' --exclude="*.zip" dist/* docs/OGN-Tracking-WGC.pdf
		mv       TRKtools.tgz dist
		zip TRKtools.zip dist/*WIN* docs/OGN-Tracking-WGC.pdf
		mv       TRKtools.zip dist
		@echo "==================== tarbal done =============================="

firmware:	dist/esp32-ogn-tracker-bin.tgz

dist/esp32-ogn-tracker-bin.tgz:	$(TRACKERSRC)/build/esp32-ogn-tracker.elf
		@echo "==============================================================="
		@echo "   Get a copy of the firmware into the distribution directory  "
		@echo "   ----------------------------------------------------------  "
		cd $(TRACKERSRC) && pwd && bash bin-arch.sh && mv *tgz ../TRKSsrc/dist/
		@echo "==============================================================="
		

clean:		cleanlocal cleanfai

cleanlocal:
		rm -rf *.output dist/TRKsetup* dist/VALI-AVX.Linux* dist/VALI-AVX.WIN* dist/VALI-AVX dist/TRKtools* dist/vali* *.spec build/ dist/build/ dist/*.tgz dist/*.zip dist/*template dist/README.md
cleanfai:
		ansible-playbook distclean.yml

