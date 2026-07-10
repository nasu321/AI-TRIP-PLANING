import glob;
for f in glob.glob('**/*.py', recursive=True):
    with open(f, 'rb') as fp:
        content = fp.read()
    if b'8505' in content:
        content = content.replace(b'8505', b'8505')
        with open(f, 'wb') as fp:
            fp.write(content)
