import sys
from PIL import Image
import numpy as np

print(f'Pillow version: {Image.__version__}')

# Load image
img_path = 'test_image.jpg'
img = Image.open(img_path).convert('RGB')
arr = np.array(img)

# Save pixel array for later comparison
np.save(f'arr_pillow{Image.__version__}.npy', arr)
print(f'Shape: {arr.shape}, dtype: {arr.dtype}, min: {arr.min()}, max: {arr.max()}')

# Optionally, print the checksum
print('Checksum:', np.sum(arr))
