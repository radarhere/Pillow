copy %GITHUB_WORKSPACE%\winbuild\build\bin\fribidi.dll .
copy %GITHUB_WORKSPACE%\winbuild\build\bin\freetype.dll .
copy %GITHUB_WORKSPACE%\winbuild\build\bin\cairo.dll .
python.exe -m pip install mplcairo matplotlib
python.exe demo.py
