import os, tempfile
from PIL.ImageShow import WindowsViewer

viewer = WindowsViewer()
x = viewer.get_command("Tests/images/hopper.png")
print(x)
