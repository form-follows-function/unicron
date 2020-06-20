from distutils.core import setup
import py2app
import os

plist = dict(
    CFBundleIdentifier="de.nelsonfritsch.unicron",
    LSMinimumSystemVersion="10.12.6",
    CFBundleShortVersionString="0.0.1",
    CFBundleVersion="0.0.1",
)

dataFiles = [
    'Resources/English.lproj',
]

setup(
    data_files=dataFiles,
    app=[dict(script="Unicron.py", plist=plist)]
)
