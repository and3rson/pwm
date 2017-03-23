import cursor
from xcffib.xproto import CW, ConfigWindow, GrabMode, ModMask, Atom, InputFocus, Time, EventMask


class Window(object):
    def __init__(self, wm, wid, page):
        print('New window:', wid)

        self.wm = wm
        self.conn = wm.get_conn()
        self.wid = wid
        self.page = page

        # self.ungrab_button()

        # self.grab_key(xkeysyms.keysyms['a'], xkeysyms.modmasks['control'])

    def set_attributes(self, mask, values):
        self.conn.core.ChangeWindowAttributesChecked(
            self.wid, mask, values
        ).check()

    def set_cursor(self, cursor_id):
        cursor_instance = cursor.create_font_cursor(self.conn, cursor_id)
        self.conn.core.ChangeWindowAttributesChecked(
            self.wid, CW.Cursor, [cursor_instance]
        ).check()

    def set_property(self, key, value):
        raise NotImplementedError()

    def configure(self, **kwargs):
        mask = 0
        values = []
        if 'x' in kwargs:
            mask |= ConfigWindow.X
            values.append(kwargs['x'])
        if 'y' in kwargs:
            mask |= ConfigWindow.Y
            values.append(kwargs['y'])
        if 'width' in kwargs:
            mask |= ConfigWindow.Width
            values.append(kwargs['width'])
        if 'height' in kwargs:
            mask |= ConfigWindow.Height
            values.append(kwargs['height'])
        if 'sibling' in kwargs:
            mask |= ConfigWindow.Sibling
            values.append(kwargs['sibling'])
        if 'stack_mode' in kwargs:
            mask |= ConfigWindow.StackMode
            values.append(kwargs['stack_mode'])
        self.conn.core.ConfigureWindow(self.wid, mask, values, True).check()

    def map(self):
        print('Mapping window', self.wid)
        self.conn.core.MapWindow(self.wid, True).check()

    def unmap(self):
        self.conn.core.UnmapWindow(self.wid, True).check()

    def grab_key(self, keysym, modifiers, owner_events=True, pointer_mode=GrabMode.Async, keyboard_mode=GrabMode.Async):
        code = self.wm.get_keymap().keysym_to_keycode(keysym)
        self.conn.core.GrabKey(1 if owner_events else 0, self.wid, modifiers, code, pointer_mode, keyboard_mode, True)

    def grab_button(self, button, modifiers, owner_events, event_mask, pointer_mode=GrabMode.Async, keyboard_mode=GrabMode.Async):
        self.conn.core.GrabButton(
            1 if owner_events else 0,
            self.wid,
            event_mask,
            pointer_mode,
            keyboard_mode,
            Atom._None,
            Atom._None,
            button,
            modifiers
        )

    def ungrab_button(self, button=Atom.Any, modifiers=ModMask.Any):
        self.conn.core.UngrabButton(button, self.wid, modifiers)

    def get_page(self):
        return self.page

    def focus(self):
        # PointerRoot
        print('Focusing window', self)
        # self.conn.core.SetInputFocus(InputFocus.PointerRoot, self.wid, Time.CurrentTime)
        # if self.page.current_window is not None:
        #     self.page.current_window.ungrab_button()
        # for window in self.page.get_windows():
        #     window.ungrab_button()
        # self.grab_button(Atom.Any, ModMask.Any, True, EventMask.ButtonPress | EventMask.ButtonRelease | EventMask.ButtonMotion)
        # self.unmap()
        # self.map()
        self.conn.core.SetInputFocus(InputFocus.PointerRoot, self.wid, Time.CurrentTime, True).check()

    def __repr__(self):
        return '<Window id={} page={}>'.format(
            self.wid,
            self.page.get_name()
        )

    __str__ = __repr__

    # def register_key(self, keysym, modifiers, callback):

    # def destroy(self):
    #     self.conn.core.DestroyWindow(self.wid)
