from glob import glob

for filename in glob('/**/*cairo*', recursive=True):
    print(filename)
