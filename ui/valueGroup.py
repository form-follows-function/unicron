from AppKit import NSView, NSNoBorder
from vanilla.vanillaBase import VanillaBaseObject, osVersionCurrent, osVersion10_10
from vanilla import Group, TextBox, Button, EditText, CheckBox, HorizontalLine, List
from AppKit import NSVisualEffectView

class ValueGroup(Group):
    nsViewClass = NSView
    nsVisualEffectViewClass = NSVisualEffectView

    def __init__(self, posSize, blenderMode=None, key=None, value=None):
        super().__init__(posSize)
        self._setupView(self.nsViewClass, posSize)
        self.key, self.value = key, value

        self.separator = HorizontalLine((0, 0, -0, 1))

        self.description = TextBox((0, 10, -0, 20), str(self.key))

        if isinstance(value, dict):
            pass
        elif isinstance(self.value, str) or isinstance(value, int):
            self.edit = EditText((20, 35, -0, 20),
                            text=self.value,
                            callback=self.dummyCallback)
        elif isinstance(self.value, bool):
            self.check = CheckBox((20, 35, -0, 20), "A CheckBox",
                            callback=self.dummyCallback, 
                            value=self.value)
        elif isinstance(self.value, list):               
            self.list = List((20, 35, -0, 50), items=self.value,
                                    columnDescriptions=None,
                                    showColumnTitles=False,
                                    allowsEmptySelection=False,
                                    allowsMultipleSelection=False,
                                    autohidesScrollers=True,
                                    drawFocusRing=False)

            self.list._nsObject.setBorderType_(NSNoBorder)

    def dummyCallback(self, sender):
        pass

