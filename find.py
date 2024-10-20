from glob import glob

for filename in glob('c:/**/*freetype*', recursive=True):
    print(filename)
