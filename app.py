#!/usr/bin/env python3

import xcffib
import xcffib.xproto
import xkeysyms
import cursor
from xcffib.xproto import CW, EventMask
import argparse
import yaml
from window import Window, RootWindow
from page import Page
from panel import Panel
from bus import bus
from control import Control
import panel as panel_module
import log
import os


class WindowManager(object):
    def __init__(self, args):
        self._conn = xcffib.connect()
        self._setup = self._conn.get_setup()
        self._screen = self._setup.roots[0]
        self._root_win = self._create_root_window('./arch.png')
        # self.root_win.set_bg(None)

        log.info('Display: %s', os.environ['DISPLAY'])

        self._windows = {}
        self._pages = []

        self._keymap = xkeysyms.KeyMap(self)
        self._keymap.refresh()

        self._current_page = None

        self._config = self._parse_config_file(args.config)

        self._hotkey_callbacks = {}

        self._control = Control(self)

        # log.info('Config:\n' + yaml.dump(self.config, default_flow_style=False))

        for page_config in self._config['pages']:
            self._pages.append(
                Page(self, page_config['name'], page_config['layout'])
            )

        self._current_page = self._pages[0]

        self._event_handlers = {
            xcffib.xproto.CreateNotifyEvent: self._handle_create_notification,
            xcffib.xproto.ConfigureRequestEvent: self._handle_configure_request,
            xcffib.xproto.ConfigureNotifyEvent: self._handle_configure_notification,
            xcffib.xproto.MapRequestEvent: self._handle_map_request,
            xcffib.xproto.MapNotifyEvent: self._handle_map_notification,
            xcffib.xproto.UnmapNotifyEvent: self._handle_unmap_notification,
            xcffib.xproto.DestroyNotifyEvent: self._handle_destroy_notification,
            xcffib.xproto.MappingNotifyEvent: self._handle_mapping_notification,
            xcffib.xproto.KeyPressEvent: self._handle_key_press,
            xcffib.xproto.KeyReleaseEvent: self._handle_key_release,
            xcffib.xproto.FocusInEvent: self._handle_focus_in,
            xcffib.xproto.ExposeEvent: self._handle_exposure,
        }

        # self.panel = panel.Panel(self, 0, 0, self.screen.width_in_pixels, 24)

        self._panels = []

        for panel_config in self._config['panels']:
            panel = Panel(self, panel_config['position'], panel_config['height'])

            self._panels.append(
                panel
            )

            for widget_config in panel_config['widgets']:
                widget_cls = getattr(panel_module, widget_config['name'])
                # widget = widget_cls(self)
                panel.add_widget(widget_cls, widget_config.get('args', []))

        for key_config in self._config['keys']:
            key = key_config['bind']

            key, modifiers = xkeysyms.parse_key_string(key)

            fn = key_config['action']
            if len(fn) == 1:
                fn = getattr(self._control, fn[0])
                args = ()
            else:
                fn = getattr(self._control, fn[0])(*fn[1:])
                # args = fn[1:]

            self.register_hotkey(key, modifiers, fn)

        # self.root_win.ungrab_button()
        # self.root_win.grab_button(0, ModMask.Any, True, EventMask.ButtonPress | EventMask.ButtonRelease | EventMask.ButtonMotion)
        # self.root_win.grab_button(1, ModMask.Any, True, EventMask.ButtonPress | EventMask.ButtonRelease | EventMask.ButtonMotion)

        # # self.register_hotkey(xkeysyms.keysyms['d'], xkeysyms.modmasks['control'], debug)
        # self.register_hotkey(xkeysyms.keysyms['o'], xkeysyms.modmasks['control'], select_other)
        # # self.register_hotkey(xkeysyms.keysyms['l'], xkeysyms.modmasks['control'], lay_out)
        # self.register_hotkey(xkeysyms.keysyms['p'], xkeysyms.modmasks['control'], select_prev_page)
        # self.register_hotkey(xkeysyms.keysyms['n'], xkeysyms.modmasks['control'], select_next_page)

        # self.register_hotkey(xkeysyms.keysyms['1'], xkeysyms.modmasks['control'], select_window(1))
        # self.register_hotkey(xkeysyms.keysyms['2'], xkeysyms.modmasks['control'], select_window(2))

        # self.register_hotkey(xkeysyms.keysyms['Return'], xkeysyms.modmasks['mod1'], spawn_terminal)

        # self.control.spawn('compton', '-f', '-b')(None, None)

        for autostart_conf in self._config['autostart']:
            self._control.spawn(*map(os.path.expanduser, autostart_conf['run']))(None, None)

    def _create_root_window(self, wallpaper):
        root_win = RootWindow(self, self._screen.root, None, wallpaper=wallpaper)

        root_win.set_attributes(CW.EventMask, [
            EventMask.StructureNotify |
            EventMask.SubstructureNotify |
            EventMask.SubstructureRedirect |
            EventMask.EnterWindow |
            EventMask.LeaveWindow |
            EventMask.KeyPress |
            EventMask.FocusChange |
            EventMask.Exposure
        ])
        root_win.set_cursor(cursor.FontCursor.LeftPtr)
        root_win.set_property('_NET_WM_NAME', 'UTF8_STRING', 'PWM')
        root_win.focus()

        return root_win

    def _parse_config_file(self, path):
        f = open(path, 'r')
        data = yaml.load(f.read())
        f.close()

        return data

    def _register_window(self, wid):
        if wid not in self._windows:
            self._windows[wid] = Window(self, wid, self._current_page)
            self._current_page.add_window(self._windows[wid])
            bus.fire('window:register')
        return self._windows[wid]

    def _unregister_window(self, wid):
        if wid in self._windows:
            window = self._windows[wid]
            window.get_page().remove_window(window)
            del self._windows[wid]
            bus.fire('window:unregister')
            return True
        return False

    def switch_page(self, page):
        log.debug('Switching page %s -> %s', self._current_page, page)
        self._current_page.hide()
        self._current_page = page
        self._current_page.show()

    def main(self):
        while True:
            e = self._conn.wait_for_event()
            if e.__class__ in self._event_handlers:
                log.info('Received event %s', e.__class__.__name__)
                self._event_handlers[e.__class__](e)
            else:
                log.warn('*** Unhandled event: %s', e)

    def _handle_create_notification(self, e):
        log.debug('handle_create_notification for %x', e.window)

    def _handle_configure_request(self, e):
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

        log.debug('Configure request for %s: %s', e.window, args)

        window = self._register_window(e.window)
        window.configure(**args)

        window.get_page().get_layout().lay_out()

        # count = len(self.windows)
        # win_width = int(screen.width_in_pixels / count)
        # win_height = screen.height_in_pixels

        # for i, window in enumerate(windows.values()):
        #     window.configure(x=win_width * i, y=0, width=win_width, height=win_height)

    def _handle_configure_notification(self, e):
        pass
        # self.current_page.layout.lay_out()
        # self.get_page().get_layout().lay_out()

    def _handle_map_request(self, e):
        # print('Map request for', e.window)
        if e.window in self._windows:
            window = self._register_window(e.window)
            window.map()
            self._current_page.get_layout().lay_out()

    def _handle_map_notification(self, e):
        if e.window in self._windows:
            window = self._register_window(e.window)
            self._current_page.focus_window(window)
            # window.focus()

    def _handle_unmap_notification(self, e):
        pass
        # self.current_page.get_layout().lay_out()

        # print('Unmap notify for', e.window)
        # window = get_window(e.window)
        # window.unmap()

    def _handle_destroy_notification(self, e):
        # print('Destroy notify for', e.window)
        log.debug('handle_destroy_notification for %x', e.window)
        self._unregister_window(e.window)

    def _handle_mapping_notification(self, e):
        pass

    def _handle_key_press(self, e):
        # print(e.sequence, e.state, e.detail)
        # TODO: Shift changes keysym?
        keysym = self._keymap.keycode_to_keysym(e.detail, 0)
        cbkey = (keysym, e.state)
        if cbkey in self._hotkey_callbacks:
            log.debug('Calling %s', self._hotkey_callbacks[cbkey])
            self._hotkey_callbacks[cbkey](self, cbkey)

    def _handle_key_release(self, e):
        pass

    def _handle_focus_in(self, e):
        return
        # for window in self.current_page.get_windows():
        #     if window == self.current_page.get_current_window():
        #         bus.fire('window:focus', window)

    def _handle_exposure(self, e):
        log.debug('Expose %d', e.window)
        if e.window == self._root_win.get_wid():
            # print('EXPOSE ROOT')
            self._root_win.expose()

        for panel in self._panels:
            if e.window == self._root_win.get_wid():
                panel.expose()

        self._current_page.get_layout().lay_out()

        # if e.window in self.windows:
        #     self.windows[e.window].expose()
        # if e.window == self.root_win.wid:
        #     self.root_win.expose()
        # elif e.window in 
            # print('Draw root!')
        # print(e, dir(e))

    def register_hotkey(self, keysym, modifiers, hotkey_callback):
        self._root_win.grab_key(keysym, modifiers)
        self._hotkey_callbacks[(keysym, modifiers)] = hotkey_callback

    def get_conn(self):
        return self._conn

    def get_screen(self):
        return self._screen

    def get_root_win(self):
        return self._root_win

    def get_setup(self):
        return self._setup

    def get_keymap(self):
        return self._keymap

    def get_pages(self):
        return self._pages

    def get_current_page(self):
        return self._current_page

    def get_usable_space(self):
        x, y, w, h = 0, 0, self._screen.width_in_pixels, self._screen.height_in_pixels
        for panel in self._panels:
            if panel.get_position() == 'top':
                y += panel.get_height()
                h -= panel.get_height()
            if panel.get_position() == 'bottom':
                h -= panel.get_height()
        return x, y, w, h


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True, type=str, help='Config file')
    args = parser.parse_args()
    wm = WindowManager(args)
    wm.main()
