# -*- coding: utf-8 -*-

# Written to satisfy my need for a text entry widget with autocomplete.
# Heavily borrowed ideas from http://wiki.wxpython.org/TextCtrlAutoComplete
# Raja Selvaraj <rajajs@gmail.com>

# version 0.3
#  - Edited focus loss function to work properly.
#    (It could be only problem to me since I executed on Windows)
#  - After using tab to auto-complete, one more tab will move you to next ctrl.
#  - When used tab to auto-complete, highlight the auto-complete word to dropdown box.
#  - author: Changyun Lee <python.signal@gmail.com>

# version 0.2
#  - Added option to use case sensitive matches, default is false

# version 0.1

import wx

class ACTextControl(wx.TextCtrl):
    """
    A Textcontrol that accepts a list of choices at the beginning.
    Choices are presented to the user based on string being entered.
    If a string outside the choices list is entered, option may
    be given for user to add it to list of choices.
    match_at_start - Should only choices beginning with text be shown ?
    add_option - Should user be able to add new choices
    case_sensitive - Only case sensitive matches
    """
    def __init__(self, parent, candidates=[], match_at_start = False,
                 add_option=False, case_sensitive=False):
        wx.TextCtrl.__init__(self, parent, style=wx.TE_PROCESS_ENTER)

        self.all_candidates = candidates
        self.match_at_start = match_at_start
        self.add_option = add_option
        self.case_sensitive = case_sensitive
        self.max_candidates = 5   # maximum no. of candidates to show
        self.select_candidates = []
        self.popup = ACPopup(self)

        self._set_bindings()

        self._screenheight = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
        self._popdown = True # Does the popup go down from the textctrl ?

    def _set_bindings(self):
        """
        One place to setup all the bindings
        """
        # text entry triggers update of the popup window
        self.Bind(wx.EVT_TEXT, self._on_text, self)
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down, self)

        # loss of focus should hide the popup
        self.Bind(wx.EVT_KILL_FOCUS, self._on_focus_loss)
        self.Bind(wx.EVT_SET_FOCUS, self._on_focus)
        gp = self
        while gp != None :
            gp.Bind ( wx.EVT_MOVE , self._on_focus_loss, gp)
            gp.Bind ( wx.EVT_SIZE , self._on_focus_loss, gp)
            gp = gp.GetParent()
            
    
    def SetValue(self, value):
        """
        Directly calling setvalue triggers textevent
        which results in popup appearing.
        To avoid this, call changevalue
        """
        super(ACTextControl, self).ChangeValue(value)


    def _on_text(self, event):
        """
        On text entry in the textctrl,
        Pop up the popup,
        or update candidates if its already visible
        """
        txt = self.GetValue()

        # if txt is empty (after backspace), hide popup
        if not txt:
            if self.popup.IsShown:
                self.popup.Show(False)
                event.Skip()
                return

        # select candidates
        if self.match_at_start and self.case_sensitive:
            self.select_candidates = [ch for ch in self.all_candidates
                              if ch.startswith(txt)]
        elif self.match_at_start and not self.case_sensitive:
            self.select_candidates = [ch for ch in self.all_candidates
                                      if ch.lower().startswith(txt.lower())]
        elif self.case_sensitive and not self.match_at_start:
            self.select_candidates = [ch for ch in self.all_candidates if txt in ch]
        else:
            self.select_candidates = [ch for ch in self.all_candidates if txt.lower() in ch.lower()]
            
        if len(self.select_candidates) == 0:
            if not self.add_option:
                if self.popup.IsShown():
                    self.popup.Show(False)

            else:
                display = ['Add ' + txt]
                self.popup._set_candidates(display, 'Add')
                self._resize_popup(display, txt)
                self._position_popup()
                if not self.popup.IsShown():
                    self.popup.Show()
                
        else:
            self._show_popup(self.select_candidates, txt)


    def _show_popup(self, candidates, txt):
            # set up the popup and bring it on
            self._resize_popup(candidates, txt)
            self._position_popup()

            candidates.sort()
            
            if self._popdown:
                # TODO: Allow custom ordering
                self.popup._set_candidates(candidates, txt)
                self.popup.candidatebox.SetSelection(0)
                
            else:
                candidates.reverse()
                self.popup._set_candidates(candidates, txt)
                self.popup.candidatebox.SetSelection(len(candidates)-1)

            if not self.popup.IsShown():
                self.popup.Show()
                
    def _on_focus_loss(self, event):
        """Close the popup when focus is lost"""
        if self.IsShown():
            self.popup.Show(False)
        event.Skip()
            
    def _on_focus(self, event):
        """
        When focus is gained,
        if empty, show all candidates,
        else, show matches
        """
        txt =  self.GetValue()
        if txt == '':
            self.select_candidates = self.all_candidates
            self._show_popup(self.all_candidates, '')
        else:
            self._on_text(event)

            
    def _position_popup(self):
        """Calculate position for popup and
        display it"""
        left_x, upper_y = self.GetScreenPositionTuple()
        _, height = self.GetSizeTuple()
        popup_width, popup_height = self.popupsize
        
        if upper_y + height + popup_height > self._screenheight:
            self._popdown = False
            self.popup.SetPosition((left_x, upper_y - popup_height))
        else:
            self._popdown = True
            self.popup.SetPosition((left_x, upper_y + height))


    def _resize_popup(self, candidates, entered_txt):
        """Calculate the size for the popup to
        accomodate the selected candidates"""
        # Handle empty list (no matching candidates)
        if len(candidates) == 0:
            candidate_count = 3.5 # one line
            longest = len(entered_txt) + 4 + 4 #4 for 'Add '

        else:
            # additional 3 lines needed to show all candidates without scrollbar        
            candidate_count = min(self.max_candidates, len(candidates)) + 4
            longest = max([len(candidate) for candidate in candidates]) + 6

        
        charheight = self.popup.candidatebox.GetCharHeight()
        charwidth = self.popup.candidatebox.GetCharWidth()

        self.popupsize = wx.Size( charwidth*longest, charheight*candidate_count )

        self.popup.candidatebox.SetSize(self.popupsize)
        self.popup.SetClientSize(self.popupsize)
        

    def _on_key_down(self, event):
        """Handle key presses.
        Special keys are handled appropriately.
        For other keys, the event is skipped and allowed
        to be caught by ontext event"""
        skip = True
        visible = self.popup.IsShown() 
        sel = self.popup.candidatebox.GetSelection()
        
        # Escape key closes the popup if it is visible
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            if visible:
                self.popup.Show(False)

        # Down key for navigation in list of candidates
        elif event.GetKeyCode() == wx.WXK_DOWN:
            if not visible:
                skip = False
                pass
            # 
            if sel + 1 < self.popup.candidatebox.GetItemCount():
                self.popup.candidatebox.SetSelection(sel + 1)
            else:
                skip = False

        # Up key for navigation in list of candidates
        elif event.GetKeyCode() == wx.WXK_UP:
            if not visible:
                skip = False
                pass
            if sel > -1:
                self.popup.candidatebox.SetSelection(sel - 1)
            else:
                skip = False

        # Enter - use current selection for text
        elif event.GetKeyCode() == wx.WXK_RETURN:
            if not visible:
                # TODO :
                pass
            # Add option is only displayed
            elif len(self.select_candidates) == 0:
                if self.popup.candidatebox.GetSelection() == 0:
                    self.all_candidates.append(self.GetValue())
                self.popup.Show(False)
                
            elif self.popup.candidatebox.GetSelection() == -1:
                self.popup.Show(False)

            elif self.popup.candidatebox.GetSelection() > -1:
                self.SetValue(self.select_candidates[self.popup.candidatebox.GetSelection()])
                self.SetInsertionPointEnd()
                self.popup.Show(False)

        # Tab  - set selected choice as text
        elif event.GetKeyCode() == wx.WXK_TAB:
            if visible:
                txt = self.GetValue()
                if txt == '' or txt == self.select_candidates[self.popup.candidatebox.GetSelection()]:
                    skip = True
                else:
                    self.SetValue(self.select_candidates[self.popup.candidatebox.GetSelection()])
                    # set cursor at end of text
                    self.SetInsertionPointEnd()
                    skip = False
                    self._on_focus(None)

        if skip:
            event.Skip()

    
    
            

    def get_choices(self):
        """Return the current choices.
        Useful if choices have been added by the user"""
        return self.all_candidates        

class ACPopup(wx.PopupWindow):
    """
    The popup that displays the candidates for
    autocompleting the current text in the textctrl
    """
    def __init__(self, parent):
        wx.PopupWindow.__init__(self, parent)
        self.candidatebox = wx.SimpleHtmlListBox(self, -1, choices=[])
        self.SetSize((100, 100))
        self.displayed_candidates = []
        
    def _set_candidates(self, candidates, txt):
        """
        Clear existing candidates and use the supplied candidates
        Candidates is a list of strings.
        """
        # if there is no change, do not update
        if candidates == sorted(self.displayed_candidates):
            pass

        # Remove the current candidates
        self.candidatebox.Clear()
        
        #self.candidatebox.Append(['te<b>st</b>', 'te<b>st</b>'])
        for ch in candidates:
            self.candidatebox.Append(self._htmlformat(ch, txt))

        self.displayed_candidates = candidates


    def _htmlformat(self, text, substring):
        """
        For displaying in the popup, format the text
        to highlight the substring in html
        """
        sc = len(substring) # substring count
        span_s = '<span style="color:red;font-weight:bold;">'
        span_e = '</span>'
        # empty substring
        if sc == 0:
            return text

        elif sc == 1:
            t = []
            for i in range(len(text)):
                if text[i].isupper():
                    t.append(text[i].replace(substring.upper(), span_s + substring.upper() + span_e))
                else:
                    t.append(text[i].replace(substring, span_s + substring + span_e))

            s = ''
            return s.join(t)
        else:
            i = []
            word = text
            while True:
                index = word.lower().find(substring.lower())
                if index == -1:
                    break
                else:
                    if len(i) == 0:
                        i.append(index)
                    else:
                        i.append(index+i[-1]+sc)
                    word = word[index+sc:]
            t = ''
            i.sort()
            for m in range(len(i)):
                _i = i[m]
                if m == 0:
                    t += text[:_i]+span_s+text[_i:_i+sc]+span_e
                else:
                    t += text[i[m-1]+sc:_i]+span_s+text[_i:_i+sc]+span_e
                if m == len(i)-1:
                    if _i+sc < len(text):
                        t += text[_i+sc:]
        return t

class TestFrame(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, "Test")
        panel = wx.Panel(self)
    
        candidates = ['cat', 'Cow', 'dog', 'rat', 'Raccoon', 'pig',
                   'tiger', 'elephant', 'ant',
                   'horse', 'Anteater', 'giraffe', u'테스트', u'안녕']
    
        label1 = wx.StaticText(panel, -1, 'Matches anywhere in string')
        label2 = wx.StaticText(panel, -1, 'Matches only at beginning')
        label3 = wx.StaticText(panel, -1, 'Matches at beginning, case sensitive')
        label4 = wx.StaticText(panel, -1, 'Allows new candidates to be added')
                   
        self.ctrl1 = ACTextControl(panel, candidates=candidates, add_option=False)
        self.ctrl2 = ACTextControl(panel, candidates=candidates, match_at_start=True, add_option=False)
        self.ctrl3 = ACTextControl(panel, candidates=candidates, match_at_start=True,
                              add_option=False, case_sensitive=True)
        self.ctrl4 = ACTextControl(panel, candidates=candidates, add_option=True)
        
    
        fgsizer = wx.FlexGridSizer(rows=5, cols=2, vgap=20, hgap=10)
        fgsizer.AddMany([label1, self.ctrl1,
                         label2, self.ctrl2,
                         label3, self.ctrl3,
                         label4, self.ctrl4])
        
        panel.SetAutoLayout(True)
        panel.SetSizer(fgsizer)
        fgsizer.Fit(panel)
        panel.Layout()

class TestApp(wx.App):
    def OnInit(self):
        frame = TestFrame(None, -1)
        self.SetTopWindow(frame)
        frame.SetSize((400, 250))
        frame.Show()
        return True

if __name__ == '__main__':
    app = TestApp()
    app.MainLoop()