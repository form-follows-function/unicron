from distutils.core import setup
import py2app
import os

version = '0.0.1'

plist = dict(
    CFBundleIdentifier="de.nelsonfritsch.unicron",
    LSMinimumSystemVersion="10.12.6",
    CFBundleShortVersionString=version,
    CFBundleVersion=version,
)

dataFiles = [
    'Resources/English.lproj',
]

setup(
    version=version,
    description="Unicron is an interactive utility to help manage and edit background processes on macOS. Enhancing automation and security.",
    author="Nelson Sylvest*r Fritsch",
    url="https://github.com/form-follows-function/unicron/",
    license="GPL",
    data_files=dataFiles,
    app=[dict(script="Unicron.py", plist=plist)]
)
