#!/usr/bin/python
# -*- coding: utf-8 -*-

from pprint import pprint
import math, os, subprocess, launchd, plistlib
from functools import partial
from AppKit import NSImageNameInfo, NSPopUpButton, NSNoBorder, NSAppearance, NSImage, NSImageNameStatusPartiallyAvailable, NSImageNameStatusNone, NSImageNameStatusAvailable, NSImageNameCaution, NSImageNameRefreshTemplate, NSMakeRect, NSCompositeSourceOver, NSColor, NSNoTabsNoBorder,NSUserDefaults, NSView, NSEvent, NSObject

from vanilla import Window, Group, ImageListCell, List, HorizontalLine, TextBox, Sheet, ImageView, Button, CheckBox, PopUpButton, Popover, Tabs, TextEditor, SegmentedButton, VerticalStackGroup

from ui.valueGroup import ValueGroup

class UnicronAppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, notification):
        Unicron()
        
class Unicron(object):
    def __init__(self):
        self.locations = ['User Agents', 'Global Agents',
                        'Global Daemons', 'System Agents', 'System Daemons']
        self.listItems = []
        self.selected = {}

        # Preferences
        self.homedir = os.path.expanduser('~')
        self.prefsFolder = self.homedir + "/Library/Preferences/"
        self.prefsFile = "de.nelsonfritsch.unicron.plist"

        if os.path.isfile(self.prefsFolder + self.prefsFile):
            self.prefs = self._loadPrefs(self)
        else:
            self.prefs = dict(
                showSystemWarning = True,
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
        minsize = 285
        self.w = Window((minsize, 400), 
                        'Unicron',
                        closable=True,
                        fullSizeContentView=True,
                        titleVisible=False,
                        minSize=(minsize, minsize),
                        maxSize=(600, 1200),
                        autosaveName="UnicronMainWindow")

        self.pathList = NSPopUpButton.alloc().initWithFrame_(((0, 0), (160, 20)))
        self.pathList.addItemsWithTitles_(self.locations)

        refreshIcon = NSImage.alloc().initWithSize_((32, 32))
        sourceImage = NSImage.imageNamed_(NSImageNameRefreshTemplate)

        w, h = sourceImage.size()

        if w > h:
            diffx = 0
            diffy = w - h
        else:
            diffx = h - w
            diffy = 0

        maxSize = max([w, h])
        refreshIcon.lockFocus()
        sourceImage.drawInRect_fromRect_operation_fraction_(NSMakeRect(diffx, diffy+4, 22, 22), NSMakeRect(0, 0, maxSize, maxSize), NSCompositeSourceOver, 1)
        refreshIcon.unlockFocus()
        refreshIcon.setTemplate_(True)

        toolbarItems = [
            dict(itemIdentifier="Daemons",
                label="Daemons",
                toolTip="Daemon Group",
                view=self.pathList,
                callback=self.populateList),
            dict(itemIdentifier="image",
                label="Image",
                imageObject=refreshIcon,
                callback=self.populateList),
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

        self.prefsSetStyle(self)
        
        self.w.open()


    def prefsSetStyle(self, sender):
        style = self.prefsWindow.style.getItem()
        self._changePref(self, 'windowStyle', style)

        if style == 'System':
            style = NSUserDefaults.standardUserDefaults().stringForKey_('AppleInterfaceStyle')
        if style == 'Dark':
            winAppearance = 'NSAppearanceNameVibrantDark'
        else:
            winAppearance = 'NSAppearanceNameVibrantLight'
        appearance = NSAppearance.appearanceNamed_(winAppearance)
        self.w._window.setAppearance_(appearance)
        self.prefsWindow._window.setAppearance_(appearance)


    def prefsRestoreWarnings(self, sender):
        self._changePref(self, 'showSystemWarning', True)


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
                if file.endswith('.plist'):
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


    def _loadUnloadDaemon(self, sender, command):
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

        self.populateList(self)


    def _removeDaemon(self, sender):
        self._loadUnloadDaemon(self, 'unload')
        self._loadUnloadDaemon(self, 'remove')


    # def addGroup(self, sender, key, value):

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
                self.valueGroups = []
                # Get job path and file location
                item = self.pathList.titleOfSelectedItem()

                if 'User' in item:
                    import getpass
                    username = getpass.getuser()
                    user = username
                    path = '/Users/%s/Library/Launch' % username
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
                f = open(self.selected['file'], "r")
                self.selected['raw'] = str(f.read())
                self.selected['short'] = (self.selected['name'][:32] + '…') if len(self.selected['name']) > 32 else self.selected['name']
                # Get status
                if job['image'] == NSImage.imageNamed_(NSImageNameStatusNone):
                    status = None
                else:
                    status = 'Available'
                self.selected['status'] = status

                index = sender.getSelection()[0]
                relativeRect = sender.getNSTableView().rectOfRow_(index)

                self.pop = Popover((300, 100))

                self.pop.tabs = Tabs((20, 40, -20, -20), ["Editor", "Raw View"])
                self.pop.tabs._nsObject.setTabViewType_(NSNoTabsNoBorder)

                self.pop.tabBtn = SegmentedButton((10, 10, -10, 20),
                    [dict(title="Editor"), dict(title="Raw View")],
                    callback=self._segmentPressed, selectionStyle='one')
                self.pop.tabBtn.set(0)

                self.edit = self.pop.tabs[0]

                self.rawEdit = self.pop.tabs[1]
                self.rawEdit.editor = TextEditor((0, 0, -0, -45), text=self.selected['raw'])

                self.selected['dict'] = launchd.plist.read(self.selected['name'])

                # TODO: Add stackview to scrollview as group
                # Waiting for merge into master: https://github.com/robotools/vanilla/issues/132
                self.edit.stack = VerticalStackGroup((0, 0, -0, -45))

                for idx, (key, value) in enumerate(sorted(self.selected['dict'].items())):
                    group = ValueGroup((0, 0, -0, -0), sender=self, key=key, value=value, idx=idx)
                    self.valueGroups.append(group)
                    self.edit.stack.addView(self.valueGroups[idx], 300, self.valueGroups[idx].getPosSize()[3])

                self.pop.save = Button((20, -50, -20, 40), "Save", callback=self._savePlist)
                self.pop.save.enable(False)
                self.pop.open(parentView=sender.getNSTableView(), preferredEdge='right', relativeRect=relativeRect)
        except:
            pass

    # TODO
    def _savePlist(self, sender):
        return


    def _segmentPressed(self, sender):
        self.pop.tabs.set(self.pop.tabBtn.get())


    def _menuCallback(self, sender):
        items = []

        items.append(dict(title=self.selected['short'], enabled=False))
        items.append("----")
        if self.selected['status'] == None:
            load, able = 'Load', 'Enable'
        else:
            load, able = 'Unload', 'Disable'

        loadCallback = partial(self._loadUnloadDaemon, command=load)
        ableCallback = partial(self._loadUnloadDaemon, command=able)
        items.append(dict(title=load, callback=loadCallback))
        items.append(dict(title=able, callback=ableCallback))
        items.append(dict(title="Show in Finder", callback=self._showInFinder))
        items.append(dict(title="Refresh list", callback=self.populateList))

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
