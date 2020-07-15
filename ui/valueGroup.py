from AppKit import NSView, NSNoBorder
from vanilla.vanillaBase import VanillaBaseObject, osVersionCurrent, osVersion10_10
from vanilla import Group, TextBox, Button, EditText, CheckBox, HorizontalLine, List, HelpButton
from AppKit import NSVisualEffectView

class ValueGroup(Group):
    nsViewClass = NSView
    nsVisualEffectViewClass = NSVisualEffectView

    def __init__(self, sender, posSize, blenderMode=None, key=None, value=None):
        super().__init__(posSize)
        self.sender = sender
        self._setupView(self.nsViewClass, posSize)
        self.key, self.value = key, value

        self.separator = HorizontalLine((0, 0, -0, 1))

        self.description = TextBox((0, 10, -0, 20), str(self.key))

        if isinstance(value, dict):
            # TODO: handle nested dicts in plists in UI
            pass
        elif isinstance(self.value, str) or isinstance(value, int):
            self.edit = EditText((12, 40, -0, 20),
                            text=self.value,
                            callback=self.dummyCallback)
        # TODO: for some reasons bool types are correctly passed, but not accepted by isinstace() in this case
        elif isinstance(self.value, bool):
            self.check = CheckBox((15, 40, -0, 20), key,
                            callback=self.dummyCallback, 
                            value=self.value)
        elif isinstance(self.value, list):               
            self.list = List((15, 40, -0, 20), items=self.value,
                                    columnDescriptions=None,
                                    showColumnTitles=False,
                                    allowsEmptySelection=False,
                                    allowsMultipleSelection=False,
                                    autohidesScrollers=True,
                                    drawFocusRing=False)

            self.list._nsObject.setBorderType_(NSNoBorder)

        # TODO: Parse launchd man pages for key and show documenation
        self.help = HelpButton((-21, 10, -0, 20), callback=self.dummyCallback)

    def dummyCallback(self, sender):
        pass

