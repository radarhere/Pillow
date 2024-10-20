from glob import glob

for filename in glob('/**/*fribidi*', recursive=True):
    print(filename)
