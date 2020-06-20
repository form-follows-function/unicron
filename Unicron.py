#!/usr/bin/python
# -*- coding: utf-8 -*-

from AppKit import NSApplication, NSApp, NSWindowController
from PyObjCTools import AppHelper
from main import Unicron

class UnicronController(NSWindowController):
    Unicron()
        
if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    viewController = UnicronController.alloc().initWithWindowNibName_("MainMenu")
    viewController.showWindow_(viewController)
    NSApp.activateIgnoringOtherApps_(True)
    
    AppHelper.runEventLoop()
