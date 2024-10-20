from glob import glob

for filename in glob('/**/*freetype*', recursive=True):
    print(filename)
