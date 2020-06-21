#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import math, os, subprocess, launchd, plistlib
from functools import partial
from AppKit import NSImageNameInfo, NSPopUpButton, NSNoBorder, NSImage, NSImageNameStatusPartiallyAvailable, NSImageNameStatusNone, NSImageNameStatusAvailable, NSImageNameCaution, NSAppearance
from Foundation import NSUserDefaults
from vanilla import Window, Group, ImageListCell, List, HorizontalLine, TextBox, Sheet, ImageView, Button, CheckBox, PopUpButton


class Unicron(object):
    def __init__(self):
        self.locations = ['User Agents', 'Global Agents',
                          'Global Daemons', 'System Agents', 'System Daemons']
        self.listItems = []
        self.selected = {}
        self.daemon = None

        # Preferences
        self.homedir = os.path.expanduser('~')
        self.prefsFolder = self.homedir + "/Library/Preferences/"
        self.prefsFile = "de.nelsonfritsch.unicron.plist"

        if os.path.isfile(self.prefsFolder + self.prefsFile):
            self.prefs = self._loadPrefs(self)
        else:
            self.prefs = dict(
                showSystemWarning = True,
                windowPosSize = (100.0, 100.0, 250.0, 400.0),
                windowStyle = 'System'
            )
            self._savePrefs(self)

        # Preferences Window
        self.prefsWindow = Window((300, 105), 'Preferences')

        self.styles = ['System', 'Light', 'Dark']
        self.prefsWindow.styleTxt = TextBox((10, 10, -10, 20), "Window Style:")
        self.prefsWindow.style = PopUpButton((30, 35, -10, 20), self.styles, callback=self.prefsSetStyle)

        self.prefsWindow.restore = Button((10, 75, -10, 20), 'Restore Warnings', callback=self.prefsRestoreWarnings)

        # Main Window
        self.w = Window((250, 400), 'Unicron',
                        closable=True, fullSizeContentView=True, titleVisible=False, minSize=(160, 320), maxSize=(600, 1200))

        self.pathList = NSPopUpButton.alloc().initWithFrame_(((0, 0), (160, 20)))
        self.pathList.addItemsWithTitles_(self.locations)

        toolbarItems = [
            {"itemIdentifier": "Daemons",
             "label": "Daemons",
             "toolTip": "Daemon Group",
             "view": self.pathList,
             "callback": self.populateList},
        ]
        self.w.addToolbar("Unicron Toolbar", toolbarItems=toolbarItems, displayMode="icon")

        self.w.blend = Group((0, 0, 0, 0), blendingMode='behindWindow')

        self.listColumnDescriptions = [
            {'title': '', 'key': 'image', 'width': 25, 'typingSensitive': True, 'allowsSorting': True, 'cell': ImageListCell()}, {'title': 'Name', 'key': 'name', 'typingSensitive': True, 'allowsSorting': True, }
        ]
        self.rowHeight = 20
        self.w.list = List((0, 37, -0, 0), items=self.listItems,
                           columnDescriptions=self.listColumnDescriptions,
                           showColumnTitles=True,
                           allowsEmptySelection=True,
                           allowsMultipleSelection=False,
                           autohidesScrollers=True,
                           drawFocusRing=False,
                           rowHeight=self.rowHeight,
                           selectionCallback=self._selectionCallback,
                           menuCallback=self._menuCallback)

        self.w.list._nsObject.setBorderType_(NSNoBorder)

        self.w.statusbar = Group((0, -26, 0, 0), blendingMode='behindWindow')
        self.w.statusbar.border = HorizontalLine((0, 0, 0, 1))
        
        self.w.counter = TextBox((16, -20, -16, 15), '', alignment='center', sizeStyle='small')
        self.populateList(self)
        self.w.rowIndicator = Group((0, 0, 0, 10))

        self.w.bind('move', self.windowMoved)
        self.w.bind('resize', self.windowMoved)
        self.w.setPosSize(self.prefs.get('windowPosSize'))

        self.prefsSetStyle(self)
        
        self.w.open()


    def prefsSetStyle(self, sender):
        style = self.prefsWindow.style.getItem()
        self._changePref(self, 'windowStyle', style)

        # if self.prefs.get('windowStyle'):
        if style == 'System':
            style = NSUserDefaults.standardUserDefaults().stringForKey_('AppleInterfaceStyle')
        if style == 'Dark':                
            appearance = NSAppearance.appearanceNamed_('NSAppearanceNameVibrantDark')
        else:
            appearance = NSAppearance.appearanceNamed_('NSAppearanceNameVibrantLight')
        self.w._window.setAppearance_(appearance)
        self.prefsWindow._window.setAppearance_(appearance)


    def prefsRestoreWarnings(self, sender):
        self._changePref(self, 'showSystemWarning', True)


    def windowMoved(self, sender):
        self._changePref(self, 'windowPosSize', self.w.getPosSize())


    def populateList(self, sender):
        self.selected.clear()
        self.w.list._removeSelection()
        item = self.pathList.titleOfSelectedItem()

        for i in range(len(self.w.list)):
            del self.w.list[0]

        thisItem = {}
        image = None
        id = os.getuid()
        systemWarning = "You should not edit or remove existing system's daemons. These jobs are required for a working macOS system."

        if item != 'Active Daemons':
            if item == 'User Agents':
                homedir = os.path.expanduser('~')
                path = homedir + '/Library/LaunchAgents'
                # If the folder doesn't exist in the user folder, create it
                try:
                    os.listdir(path)
                except:
                    os.mkdir(path)
            elif item == 'Global Agents':
                path = '/Library/LaunchAgents'
            elif item == 'Global Daemons':
                path = '/Library/LaunchDaemons'
            elif item == 'System Agents':
                path = '/System/Library/LaunchAgents'
                self._warning(self, systemWarning, "showSystemWarning")
            elif item == 'System Daemons':
                path = '/System/Library/LaunchDaemons'
                self._warning(self, systemWarning, "showSystemWarning")

            items = []
            files = os.listdir(path)
            count = 0

            for file in files:
                if not '.plist' in file:
                    files.remove(file)
                else:
                    file = file.replace('.plist', '')
                    try:
                        pid = launchd.LaunchdJob(file).pid
                    except:
                        pid = False
                    if launchd.LaunchdJob(file).exists() and pid != None:
                        image = NSImage.imageNamed_(NSImageNameStatusAvailable)
                    elif launchd.LaunchdJob(file).exists() and pid == None:
                        image = NSImage.imageNamed_(NSImageNameStatusPartiallyAvailable)
                    else:
                        image = NSImage.imageNamed_(NSImageNameStatusNone)
                    state = True
                    thisItem['image'] = image
                    thisItem['name'] = file
                    self.w.list.append(thisItem)
                    count += 1
            self.w.counter.set(str(count) + ' Jobs')


    def _showInFinder(self, sender):
        file = self.selected['file']
        subprocess.call(['open', '-R', '%s' % file], cwd='/',
                        shell=False, universal_newlines=False)


    def _loadUnloadDaemon(self, sender):
        self.w.list.scrollToSelection()
        name = self.selected['name']
        path = self.selected['file']

        if bool(launchd.LaunchdJob(name).exists()):
            try:
                subprocess.call(['launchctl', 'unload', '%s' % path], cwd='/', shell=False, universal_newlines=False)
                self.populateList(self)
            except:
                return
        else:
            try:
                subprocess.call(['launchctl', 'load', '%s' % path], cwd='/', shell=False, universal_newlines=False)
                self.populateList(self)
            except:
                return
                

    def _removeDaemon(self, sender):
        self.w.list.scrollToSelection()
        name = self.selected['name']
        path = self.selected['file']

        if bool(launchd.LaunchdJob(name).exists()):
            try:
                subprocess.call(['launchctl', 'unload', '%s' % path], cwd='/', shell=False, universal_newlines=False)
                subprocess.call(['launchctl', 'remove', '%s' % path], cwd='/', shell=False, universal_newlines=False)
                self.populateList(self)
            except:
                return


    def _selectionCallback(self, sender):
        try:
            if not self.w.list.getSelection():
                # Application did not finish loading yet
                pass
            else:
                # Get job name
                self.selected.clear()
                job = sender.get()[self.w.list.getSelection()[0]]
                self.selected['name'] = job['name']
                
                # Get job path and file location
                item = self.pathList.titleOfSelectedItem()

                if 'User' in item:
                    import getpass
                    username = getpass.getuser()
                    user = username
                    path = 'Users/%s/Library/Launch' % username
                elif 'Global' in item:
                    user = 'All users'
                    path = '/Library/Launch'
                elif 'System' in item:
                    user = 'System'
                    path = '/System/Library/Launch'
                if 'Agents' in item:
                    path += 'Agents/'
                else:
                    path += 'Daemons/'

                self.selected['path'] = path
                self.selected['file'] = str(self.selected['path'].replace(' ', '\ ')) + job['name'].replace(' ', '\ ') + '.plist'
                
                # Get status
                if job['image'] == NSImage.imageNamed_(NSImageNameStatusNone):
                    status = None
                else:
                    status = 'Available'
                self.selected['status'] = status
        except:
            pass
   

    def _menuCallback(self, sender):
        items = []
        if self.selected['status'] == None:
            load = 'Load'
            items.append(dict(title=load, callback=self._loadUnloadDaemon))
        else:
            load = 'Unload'
            items.append(dict(title=load, callback=self._loadUnloadDaemon))
            items.append(dict(title="Remove", callback=self._removeDaemon))

        items.append(dict(title="Refresh list", callback=self.populateList))
        items.append(dict(title="Show in Finder", callback=self._showInFinder))

        return items


    def _loadPrefs(self, sender):
        with open(self.prefsFolder + self.prefsFile, 'rb') as fp:
            self.prefs = plistlib.load(fp)
        return self.prefs


    def _savePrefs(self, sender):
        with open(self.prefsFolder + self.prefsFile, 'wb') as fp:
            plistlib.dump(self.prefs, fp)


    def _changePref(self, sender, key, value):
        self.prefs[key] = value
        self._savePrefs(self)


    def _warning(self, sender, warning, prefKey):
        if self.prefs.get(prefKey):
            self.warning = Sheet((400, 140), self.w)
            self.warning.img = ImageView((10, 10, 60, 60))
            self.warning.img.setImage(imageNamed=NSImageNameCaution)
            self.warning.txt = TextBox((70, 10, -10, -40), "Warning\n"+warning)

            callback = partial(self._changePref, key=prefKey, value=not self.prefs.get(prefKey))
            self.warning.check = CheckBox((70, 80, -10, 20), "Always show this warning", value=self.prefs.get(prefKey), callback=callback)

            self.warning.closeButton = Button((10, 110, -10, 20), "I understand", callback=self._closeWarning)
            self.warning.setDefaultButton(self.warning.closeButton)
            self.warning.center()
            self.w.list.enable(False)
            self.warning.open()

    
    def _closeWarning(self, sender):
        self.warning.close()
        self.w.list.enable(True)
        del self.warning
