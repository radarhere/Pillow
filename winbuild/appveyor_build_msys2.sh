#!/bin/sh

cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/msys64/mingw32/bin/libfreetype.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/msys64/mingw32/bin/freetype.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/pillow/freetype.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/pillow/build/lib.mingw-3.7/PIL/freetype.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/pillow/build/lib.mingw-3.7/PIL/libfreetype.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/pillow/build/lib.mingw-3.7/PIL/libfreetype-6.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/pillow/winbuild/freetype.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/pillow/winbuild/libfreetype.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/pillow/winbuild/libfreetype-6.dll
cd /c/pillow && /mingw32/$EXECUTABLE setup.py install
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/msys64/mingw32/bin/libfreetype.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/msys64/mingw32/bin/freetype.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/pillow/freetype.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/pillow/build/lib.mingw-3.7/PIL/freetype.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/pillow/build/lib.mingw-3.7/PIL/libfreetype.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/pillow/build/lib.mingw-3.7/PIL/libfreetype-6.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/pillow/winbuild/freetype.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/pillow/winbuild/libfreetype.dll
cp /c/msys64/mingw32/bin/libfreetype-6.dll /c/pillow/winbuild/libfreetype-6.dll
/mingw32/$EXECUTABLE -c "from PIL import _imaging;import os, shutil;shutil.copy('C:/msys64/mingw32/bin/libfreetype-6.dll', os.path.join(os.path.dirname(_imaging.__file__), 'freetype.dll'));"
/mingw32/$EXECUTABLE -c "from PIL import _imaging;import os, shutil;shutil.copy('C:/msys64/mingw32/bin/libfreetype-6.dll', os.path.join(os.path.dirname(_imaging.__file__), 'libfreetype.dll'));"
/mingw32/$EXECUTABLE -c "from PIL import _imaging;import os, shutil;print(['torch',_imaging.__file__]);print(os.listdir(os.path.dirname(_imaging.__file__)));shutil.copy('C:/msys64/mingw32/bin/libfreetype-6.dll', os.path.join(os.path.dirname(_imaging.__file__), 'libfreetype-6.dll'));"
