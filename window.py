import cursor
from xcffib.xproto import CW, ConfigWindow, GrabMode
import xkeysyms


class Window(object):
    def __init__(self, wm, wid):
        print('New window:', wid)

        self.wm = wm
        self.conn = wm.get_conn()
        self.wid = wid

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
        print(mask, values)
        self.conn.core.ConfigureWindow(self.wid, mask, values, True).check()

    def map(self):
        print('Mapping window', self.wid)
        self.conn.core.MapWindow(self.wid, True).check()

    def unmap(self):
        self.conn.core.UnmapWindow(self.wid)

    def grab_key(self, keysym, modifiers, owner_events=True, pointer_mode=GrabMode.Async, keyboard_mode=GrabMode.Async):
        code = self.wm.get_keymap().keysym_to_keycode(keysym)
        print((1 if owner_events else 0, self.wid, modifiers, code, pointer_mode, keyboard_mode, True))
        self.conn.core.GrabKey(1 if owner_events else 0, self.wid, modifiers, code, pointer_mode, keyboard_mode, True)

    # def register_key(self, keysym, modifiers, callback):

    # def destroy(self):
    #     self.conn.core.DestroyWindow(self.wid)
