#!/bin/bash
rm -r build/*
cp *.template dist/
cp README*    dist/
pyinstaller -F --noconfirm --clean --key OGNOGNOGNOGNOGN --name TRKsetup.$(uname -s)$(uname -m) TRKsetup.py
pyinstaller -F --noconfirm --clean --key OGNOGNOGNOGNOGN --name VALI-AVX.$(uname -s)$(uname -m) VALI-AVX.py
rm -r build/*
