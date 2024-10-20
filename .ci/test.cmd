copy %GITHUB_WORKSPACE%\winbuild\build\bin\fribidi.dll .
dir /s c:/ freetype.dll
dir /s c:/ cairo.dll
python.exe -m pip install mplcairo matplotlib
python.exe demo.py
