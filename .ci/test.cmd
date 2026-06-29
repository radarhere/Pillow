python.exe -c "from PIL import Image"
IF ERRORLEVEL 1 EXIT /B
python.exe -c "from PIL import ImagePath;ImagePath.Path(0x4000000000000000)"
