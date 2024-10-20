from glob import glob

for filename in glob('/**/*raqm*', recursive=True):
    print(filename)
