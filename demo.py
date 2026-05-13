import os, shutil, tempfile
from PIL.ImageShow import WindowsViewer

viewer = WindowsViewer()
y = 'Tests/images/h\"oppe\"r.png'
shutil.move("Tests/images/hopper.png", y)
x = viewer.get_command(y)
print(x)
