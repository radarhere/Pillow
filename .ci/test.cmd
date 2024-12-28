python.exe -c "from PIL import Image"
IF ERRORLEVEL 1 EXIT /B
python.exe -c "from PIL import Image;Image.open('clusterfuzz-testcase-minimized-fuzz_pillow-5015640213159936').load()"
