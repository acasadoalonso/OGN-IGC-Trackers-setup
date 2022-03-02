export PATH="$PATH:/C/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.30.30705/bin/HostX86/x64/"
export include="C:\Program*Files/Microsoft*Visual*Studio/2022/Community/VC/Tools/MSVC/14.30.30705/include:C:\Program*Files\Microsoft*Visual*Studio\2022\Community\VC\Tools\MSVC\14.30.30705\include:Z:\Documents\OGN\src\TRKSsrc\python-mbedtls\include:Z:\Documents\OGN\src\mbedtls\include" 
echo $include
cl.exe  vali-avx.cc 

#C:\Program*Files\Microsoft*Visual*Studio\2022\Community\VC\Tools\MSVC\14.30.30705\bin\HostX86\x64\link.exe /nologo /INCREMENTAL:NO /LTCG /DLL /MANIFEST:EMBED,ID=2 /MANIFESTUAC:NO /LIBPATH:Z:\Documents\OGN\src\mbedtls\visualc\VS2010\x64\Release /LIBPATH:C:\Users\acasa\AppData\Local\Programs\Python\Python310\libs /LIBPATH:Z:\Documents\OGN\src\mbedtls\visualc\VS2010\x64\Release\mbedTLS.lib  vali-avx.obj
