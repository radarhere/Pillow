copy %GITHUB_WORKSPACE%\winbuild\build\bin\fribidi.dll .
copy %GITHUB_WORKSPACE%\winbuild\build\lib\freetype.lib .
python.exe -m pip install mplcairo matplotlib
python.exe demo.py
