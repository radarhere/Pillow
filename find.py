from glob import glob

for filename in glob('c:/**/*cairo*', recursive=True):
    print(filename)
