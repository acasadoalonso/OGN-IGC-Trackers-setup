#!/bin/bash
rm -r build/*
cp *.template dist/
cp README*    dist/
pyinstaller -F --noconfirm --clean --key OGNOGNOGNOGNOGN --name TRKsetup.WIN TRKsetup.py
pyinstaller -F --noconfirm --clean --key OGNOGNOGNOGNOGN --name VALI-AVX.WIN VALI-AVX.py
rm -r build/*
