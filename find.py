from glob import glob

for filename in glob('c:/**/*fribidi*', recursive=True):
    print(filename)
