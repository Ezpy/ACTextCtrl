Auto Complete TextCtrl for WxPython
==========
wxpython TextCtrl with smart auto-completion (Edited Version)

This is an edited version of RajaS work in https://github.com/RajaS/ACTextCtrl.
The widget is designed to present a textctrl into which the user starts typing.

[ previous ]

Matches (configurable to matches at beginning or matches anywhere) to the typed text will appear in a dropdown box.
Up and down arrow keys can be used to navigate among the matches.
Enter key will populate the textctrl with the selected match.
Tab key will expand the entered text to the current match.
When text is entered that does not have a match, an option exists to allow the user to add this text to the choices available.

[ now ]
Edited focus loss function to work properly. (It could be only problem to me since I executed on Windows)
After using tab to auto-complete, one more tab will move you to next ctrl. 
When used tab to auto-complete, highlight the auto-complete word to dropdown box.

- Tip
Unicode works perfect ! Just add unicode type to candidates list.

I have tested on Windows 8 with Python 2.7 and Wxpython 3.0. I hope this works fine on other operation system.

![alt tag](https://github.com/Ezpy/ACTextCtrl/blob/master/screenshot.png)
