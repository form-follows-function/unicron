from __future__ import print_function

from AppKit import NSObject
from PyObjCTools import AppHelper
from main import Unicron


class UnicronAppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        Unicron()


if __name__ == "__main__":
    AppHelper.runEventLoop()
