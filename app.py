#!/usr/bin/env python3

import xcffib
import xcffib.xproto
import xkeysyms
from window import Window
import cursor
from xcffib.xproto import CW, EventMask
import argparse
import yaml
import page
# from xcursors import Cursors
# import Xlib.rdb


class WindowManager(object):
    def __init__(self, args):
        self.conn = xcffib.connect()
        self.setup = self.conn.get_setup()
        self.screen = self.setup.roots[0]
        self.root_win = self._create_root_window()

        self.windows = {}
        self.pages = []

        self.keymap = xkeysyms.KeyMap(self)
        self.keymap.refresh()

        self.current_page = None

        self.config = self._parse_config_file(args.config)

        self.hotkey_callbacks = {}

        print('Config:\n' + yaml.dump(self.config, default_flow_style=False))

        for page_config in self.config['pages']:
            self.pages.append(
                page.Page(self, page_config['name'], page_config['layout'])
            )

        self.current_page = self.pages[0]

        self.event_handlers = {
            xcffib.xproto.ConfigureRequestEvent: self.handle_configure_request,
            xcffib.xproto.ConfigureNotifyEvent: self.handle_configure_notification,
            xcffib.xproto.MapRequestEvent: self.handle_map_request,
            xcffib.xproto.MapNotifyEvent: self.handle_map_notification,
            xcffib.xproto.UnmapNotifyEvent: self.handle_unmap_notification,
            xcffib.xproto.DestroyNotifyEvent: self.handle_destroy_notification,
            xcffib.xproto.KeyPressEvent: self.handle_key_press,
            xcffib.xproto.KeyReleaseEvent: self.handle_key_release
        }

        def do_stuff(wm, cbkey):
            print('Doing stuff!')

        self.register_hotkey(xkeysyms.keysyms['n'], xkeysyms.modmasks['control'], do_stuff)

    def _create_root_window(self):
        root_win = Window(self, self.screen.root)

        root_win.set_attributes(CW.EventMask, [
            EventMask.StructureNotify |
            EventMask.SubstructureNotify |
            EventMask.SubstructureRedirect |
            EventMask.EnterWindow |
            EventMask.LeaveWindow
            # EventMask.KeyPress
        ])
        root_win.set_cursor(cursor.FontCursor.LeftPtr)

        return root_win

    def _parse_config_file(self, path):
        f = open(path, 'r')
        data = yaml.load(f.read())
        f.close()

        return data

    def register_window(self, wid):
        if wid not in self.windows:
            self.windows[wid] = Window(self, wid)
        return self.windows[wid]

    def unregister_window(self, wid):
        if wid in self.windows:
            del self.windows[wid]
            return True
        return False

    def main(self):
        while True:
            e = self.conn.wait_for_event()
            if e.__class__ in self.event_handlers:
                print('Received', e.__class__.__name__)
                self.event_handlers[e.__class__](e)
            else:
                print('*** Unhandled event:', e)

    def handle_configure_request(self, e):
        args = {}

        if xcffib.xproto.ConfigWindow.X & e.value_mask:
            args['x'] = e.x
        if xcffib.xproto.ConfigWindow.Y & e.value_mask:
            args['y'] = e.y
        if xcffib.xproto.ConfigWindow.Width & e.value_mask:
            args['width'] = e.width
        if xcffib.xproto.ConfigWindow.Height & e.value_mask:
            args['height'] = e.height
        if xcffib.xproto.ConfigWindow.Sibling & e.value_mask:
            args['sibling'] = e.above
        if xcffib.xproto.ConfigWindow.StackMode & e.value_mask:
            args['stack_mode'] = e.stack_mode

        print('Configure request for', e.window, '->', args)

        window = self.register_window(e.window)
        window.configure(**args)

        # count = len(self.windows)
        # win_width = int(screen.width_in_pixels / count)
        # win_height = screen.height_in_pixels

        # for i, window in enumerate(windows.values()):
        #     window.configure(x=win_width * i, y=0, width=win_width, height=win_height)

    def handle_configure_notification(self, e):
        pass

    def handle_map_request(self, e):
        # print('Map request for', e.window)
        window = self.register_window(e.window)
        window.map()

    def handle_map_notification(self, e):
        pass

    def handle_unmap_notification(self, e):
        pass
        # print('Unmap notify for', e.window)
        # window = get_window(e.window)
        # window.unmap()

    def handle_destroy_notification(self, e):
        # print('Destroy notify for', e.window)
        self.unregister_window(e.window)

    def handle_key_press(self, e):
        # print(e.sequence, e.state, e.detail)
        # TODO: Shift changes keysym?
        keysym = self.keymap.keycode_to_keysym(e.detail, 0)
        cbkey = (keysym, e.state)
        if cbkey in self.hotkey_callbacks:
            self.hotkey_callbacks[cbkey](self, cbkey)

    def handle_key_release(self, e):
        pass

    def register_hotkey(self, keysym, modifiers, hotkey_callback):
        self.root_win.grab_key(keysym, modifiers)
        self.hotkey_callbacks[(keysym, modifiers)] = hotkey_callback

    def get_conn(self):
        return self.conn

    def get_screen(self):
        return self.screen

    def get_setup(self):
        return self.setup

    def get_keymap(self):
        return self.keymap


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True, type=str, help='Config file')
    args = parser.parse_args()
    wm = WindowManager(args)
    wm.main()
