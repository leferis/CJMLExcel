import PyInstaller.__main__

# Use the prepared spec so `datas` (assets/) are bundled into the executable
PyInstaller.__main__.run([
    'parser.spec',
    '--noconfirm',
])