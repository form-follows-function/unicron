from AppKit import NSView, NSNoBorder, NSPopUpButton, NSVisualEffectView
from vanilla.vanillaBase import VanillaBaseObject, osVersionCurrent, osVersion10_10
from vanilla import FloatingWindow, Group, TextBox, Button, EditText, CheckBox, HorizontalLine, List, HelpButton, Window, TextEditor
import pprint
import subprocess
from docstrings import docstring


class ValueGroup(Group):
    nsViewClass = NSView
    nsVisualEffectViewClass = NSVisualEffectView

    def __init__(self, posSize, sender=None, blenderMode=None, key=None, value=None, idx=0):
        super().__init__(posSize)
        self._setupView(self.nsViewClass, posSize)
        self.sender, self.key, self.value, self.idx = sender, key, value, idx

        if self.idx > 0:
            self.separator = HorizontalLine((0, 0, -0, 1))

        self.help = HelpButton((0, 10, 21, 20), callback=self._helpCallback)
        try:
            docstring[self.key]
        except:
            self.help.enable(False)

        description = TextBox((60, 10, -0, 20), str(self.key))

        if isinstance(value, dict):
            self.description = description
            # TODO: Recursive evaluation of nested dicts
            pass

        elif isinstance(self.value, str) or (isinstance(value, int) and not isinstance(value, bool)):
            self.description = description
            self.edit = EditText((10, 40, -0, 20),
                            text=self.value,
                            callback=self._dummyCallback)
            self.resize(self.getPosSize()[2], 80)

        elif isinstance(self.value, bool):
            self.check = CheckBox((60, 10, -0, 20), key,
                            callback=self._dummyCallback, 
                            value=self.value)
            self.resize(self.getPosSize()[2], 40)

        elif isinstance(self.value, list):
            values = self.getValues(self.value)

            self.description = description
            self.list = List((10, 40, -0, 80), items=self.value,
                                    columnDescriptions=None,
                                    showColumnTitles=False,
                                    allowsEmptySelection=False,
                                    allowsMultipleSelection=False,
                                    autohidesScrollers=True,
                                    drawFocusRing=False)
            self.list._nsObject.setBorderType_(NSNoBorder)
            self.resize(self.getPosSize()[2], 120)

    def _dummyCallback(self, sender):
        pass

    def run_command(self, sender, command):
        if self.fw:
            self.fw.close()

        p = subprocess.Popen(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
        return iter(p.stdout.readline, b'')


    def getValues(self, name):
        try:
            lambda v: True if 'values'in sorted(docstring[name].keys()) else False
            if v: 
                return docstring[name]['values']
        except:
            return


    def getContent(self, name):
        output = docstring[name]['description']
        
        if 'values' in docstring[name]:
            output += "\n\n\nValues:"
            for value in docstring[name]['values']:
                output += "\n\n" + value + ":\n" + docstring[name]['values'][value]['description']


        return output

    def _helpCallback(self, sender):

        self.w = Window((300, 300), "Help", closable=True, fullSizeContentView=True, titleVisible=False, minSize=(300, 300), maxSize=(600, 800))

        self.topics=[]
        for key in docstring.keys():
            self.topics.append(key)

        self.pathList = NSPopUpButton.alloc().initWithFrame_(((0, 0), (160, 20)))
        self.pathList.addItemsWithTitles_(self.topics)

        toolbarItems = [
            dict(itemIdentifier="Help",
                label="Help",
                toolTip="Topic",
                view=self.pathList,
                callback=self._getTopic),
        ]
        self.w.addToolbar("Help Toolbar", toolbarItems=toolbarItems, displayMode="icon")

        output = self.getContent(self.key)
        self.w.helptext = TextEditor((10, 47, -10, -10), text=output, readOnly=True)
        self.w.helptext._nsObject.setBorderType_(NSNoBorder)
        self.w.helptext.getNSTextView().setDrawsBackground_(False)
        self.w.helptext.getNSScrollView().setDrawsBackground_(False)

        self.w.open()

    def _getTopic(self, sender):
        selected = self.pathList.titleOfSelectedItem()
        selected = self.getContent(selected)
        self.w.helptext.set(selected)