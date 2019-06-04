from __future__ import print_function

import os, sys
import vanilla


try:
    reload(vanilla)
except NameError:
    # the built-in 'reload' was moved to importlib with Python 3.4
    from importlib import reload
    reload(vanilla)
from vanilla.py23 import range
from vanilla import *
from main import *


import objc
objc.setVerbose(True)
vanillaPath = os.path.realpath(vanilla.__file__)
vanillaPath = os.path.dirname(os.path.dirname(os.path.dirname(vanillaPath)))
iconPath = os.path.join(vanillaPath, "Data", "testIcon.tif")
iconName = None

if not os.path.exists(iconPath):
    iconPath = None
    iconName = NSImageNameInfo


class Test(object):
    def __init__(self):
        Unicron()

    def openTestCallback(self, sender):
        title = sender.getTitle()


if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)
