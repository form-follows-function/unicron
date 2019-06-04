#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import math, os, subprocess, launchd
from PyObjCTools import AppHelper
from AppKit import *
from vanilla import *


class Unicron(object):
    def __init__(self):
        self.locations = ['User Agents', 'Global Agents',
                          'Global Daemons', 'System Agents', 'System Daemons']
        self.listItems = []
        self.selected = {}
        self.daemon = None

        # WINDOW SETUP
        self.w = Window((250, 400), 'Unicron',
                        closable=True, fullSizeContentView=True, minSize=(200, 320), maxSize=(600, 1200))
                        
        self.w.blend = Group((0, 0, 0, 0), blendingMode='behindWindow')

        self.w.pathList = PopUpButton(
            (8, 25, -55, 20), self.locations, callback=self.populateList)

        self.w.refresh = ImageButton((-55, 25, -25, 20), bordered=False, imageNamed=NSImageNameRefreshTemplate, callback=self.populateList)

        self.listColumnDescriptions = [
            {'title': '', 'key': 'image', 'width': 25, 'typingSensitive': True, 'allowsSorting': True, 'cell': ImageListCell()}, {'title': 'Name', 'key': 'name', 'typingSensitive': True, 'allowsSorting': True, }
        ]
        self.rowHeight = 20
        self.w.list = List((0, 55, -0, 0), items=self.listItems,
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
        item = self.w.pathList.getItem()

        for i in range(len(self.w.list)):
            del self.w.list[0]

        thisItem = {}
        image = None
        id = os.getuid()

        if item != 'Active Daemons':
            if item == 'User Agents':
                homedir = os.path.expanduser('~')
                path = homedir + '/Library/LaunchAgents'
            elif item == 'Global Agents':
                path = '/Library/LaunchAgents'
            elif item == 'Global Daemons':
                path = '/Library/LaunchDaemons'
            elif item == 'System Agents':
                path = '/System/Library/LaunchAgents'
            elif item == 'System Daemons':
                path = '/System/Library/LaunchDaemons'

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
            except:
                return
        else:
            try:
                subprocess.call(['launchctl', 'load', '%s' % path], cwd='/', shell=False, universal_newlines=False)
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
                item = self.w.pathList.getItem()

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
            dict(title="Show in Finder", callback=self._showInFinder)
        ]

        return items

