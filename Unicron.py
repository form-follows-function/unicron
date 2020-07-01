#!/usr/bin/python
# -*- coding: utf-8 -*-
from Cocoa import objc
from AppKit import NSApplication, NSWindowController
from PyObjCTools import AppHelper
from main import Unicron

class UnicronController(NSWindowController):
    def windowDidLoad(self):
        NSWindowController.windowDidLoad(self)
        self.Unicron = Unicron()

    @objc.IBAction
    def openGithub_(self, sender):
        import webbrowser
        webbrowser.open('https://github.com/form-follows-function/unicron', new=2)

    @objc.IBAction
    def showPrefs_(self, sender):
        self.Unicron.prefsWindow.open()

        
if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    viewController = UnicronController.alloc().initWithWindowNibName_("MainMenu")
    viewController.showWindow_(viewController)
    app.activateIgnoringOtherApps_(True)
    
    AppHelper.runEventLoop()
