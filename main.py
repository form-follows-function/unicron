#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import math, os, subprocess, launchd
from PyObjCTools import AppHelper
from AppKit import NSImageNameInfo, NSPopUpButton, NSNoBorder, NSImage, NSImageNameStatusPartiallyAvailable, NSImageNameStatusNone, NSImageNameStatusAvailable, NSImageNameCaution
from vanilla import Window, Group, ImageListCell, List, HorizontalLine, TextBox, Sheet, ImageView, Button, CheckBox


class Unicron(object):
    def __init__(self):
        self.locations = ['User Agents', 'Global Agents',
                          'Global Daemons', 'System Agents', 'System Daemons']
        self.listItems = []
        self.selected = {}
        self.daemon = None

        # WINDOW SETUP
        self.w = Window((250, 400), 'Unicron',
                        closable=True, fullSizeContentView=True, titleVisible=False, minSize=(160, 320), maxSize=(600, 1200))

        self.pathList = NSPopUpButton.alloc().initWithFrame_(((0, 0), (160, 20)))
        self.pathList.addItemsWithTitles_(self.locations)

        toolbarItems = [
            {"itemIdentifier": "Daemons",
             "label": "Daemons",
             "toolTip": "Location of daemons",
             "view": self.pathList,
             "callback": self.populateList},
        ]
        self.w.addToolbar("Vanilla Test Toolbar", toolbarItems=toolbarItems, displayMode="label")

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

        self.w.open()


    def populateList(self, sender):
        self.selected.clear()
        self.w.list._removeSelection()
        item = self.pathList.titleOfSelectedItem()

        for i in range(len(self.w.list)):
            del self.w.list[0]

        thisItem = {}
        image = None
        id = os.getuid()
        warning = "You should not edit or remove existing system's daemons. These jobs are required for a working macOS system."

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
                self._warning(self, warning)
            elif item == 'System Daemons':
                path = '/System/Library/LaunchDaemons'
                self._warning(self, warning)

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
        if self.selected['status'] == None:
            load = 'Load'
        else:
            load = 'Unload'

        items = [
            dict(title=load, callback=self._loadUnloadDaemon),
            dict(title="Refresh list", callback=self.populateList),
            dict(title="Show in Finder", callback=self._showInFinder)
        ]

        return items


    def _warning(self, sender, warning):
        self.warning = Window((450, 110), title="", closable=False, miniaturizable=False, fullSizeContentView=True)
        self.warning.img = ImageView((10, 10, 50, 50))
        self.warning.img.setImage(imageNamed=NSImageNameCaution)
        self.warning.txt = TextBox((70, 10, -10, -40), "Warning\n"+warning)
        self.warning.closeButton = Button((10, -30, -10, 20), "I understand", callback=self._closeWarning)
        self.warning.setDefaultButton(self.warning.closeButton)
        self.warning.center()
        self.w.list.enable(False)
        self.warning.open() 

    
    def _closeWarning(self, sender):
        self.warning.close()
        self.w.list.enable(True)
        del self.warning
