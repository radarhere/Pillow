from PIL import Image
try:
  Image.new('RGB', (1, 1)).save('out.avif')
except RuntimeError:
  pass
