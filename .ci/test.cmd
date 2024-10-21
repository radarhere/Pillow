copy %GITHUB_WORKSPACE%\winbuild\build\bin\fribidi.dll .
copy %GITHUB_WORKSPACE%\winbuild\build\bin\fribidi.dll libfribidi.dll
copy %GITHUB_WORKSPACE%\winbuild\build\bin\fribidi.dll libfribidi-0.dll
copy %GITHUB_WORKSPACE%\winbuild\build\lib\brotlicommon.lib .
copy %GITHUB_WORKSPACE%\winbuild\build\lib\brotlidec.lib .
copy %GITHUB_WORKSPACE%\winbuild\build\lib\freetype.lib .
copy %GITHUB_WORKSPACE%\winbuild\build\lib\harfbuzz.lib .
copy %GITHUB_WORKSPACE%\libraqm-0.dll libraqm.dll

dir %GITHUB_WORKSPACE%\winbuild\build\bin
dir %GITHUB_WORKSPACE%\winbuild\build\lib

python.exe -m pip install mplcairo matplotlib
python.exe demo.py
