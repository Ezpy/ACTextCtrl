Auto Complete TextCtrl for WxPython
==========
wxpython TextCtrl with smart autocompletion (Edited Version)

This is an edited version of RajaS work in https://github.com/RajaS/ACTextCtrl.
The widget is designed to present a textctrl into which the user starts typing.

[ previous ]

■ Matches (configurable to matches at beginning or matches anywhere) to the typed text will appear in a dropdown box.
■ Up and down arrow keys can be used to navigate among the matches.
■ Enter key will populate the textctrl with the selected match.
■ Tab key will expand the entered text to the current match.
■ When text is entered that does not have a match, an option exists to allow the user to add this text to the choices available.

[ now ]

■ Edited focus loss function to work properly. (It could be only problem to me since I executed on Windows)
■ Tab problem
■ Highlight problem

I have tested on Windows 8 with Python 2.7 and Wxpython 3.0. I hope this works fine on other operation system.
