python.exe -c "from PIL import Image"
IF ERRORLEVEL 1 EXIT /B
python.exe Tests/test_file_libtiff.py
