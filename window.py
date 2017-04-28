import cursor
from xcffib.xproto import CW, ConfigWindow, GrabMode, ModMask, Atom, InputFocus, Time, PropMode, WindowError
from bus import bus
# from drawing import Painter, CairoPainter
import log


class Window(object):
    def __init__(self, wm, wid, page):
        log.info('New window: %d', wid)

        self._wm = wm
        self._conn = wm.get_conn()
        self._wid = wid
        self._page = page

        self._mapped = False

        # self.ungrab_button()

        # self.grab_key(xkeysyms.keysyms['a'], xkeysyms.modmasks['control'])

    def set_attributes(self, mask, values):
        self._conn.core.ChangeWindowAttributesChecked(
            self._wid, mask, values
        ).check()

    def set_cursor(self, cursor_id):
        cursor_instance = cursor.create_font_cursor(self._conn, cursor_id)
        self._conn.core.ChangeWindowAttributesChecked(
            self._wid, CW.Cursor, [cursor_instance]
        ).check()

    def set_property(self, key, type, value):
        # TODO: Cache atoms
        self._conn.core.ChangeProperty(
            PropMode.Replace,
            self._wid,
            self._conn.core.InternAtom(False, len(key), key).reply().atom,
            self._conn.core.InternAtom(False, len(type), type).reply().atom,
            8,
            len(value),
            value,
            True
        ).check()

    def get_property(self, key, type):
        # TODO: Cache atoms
        return self._conn.core.GetProperty(
            False,
            self._wid,
            self._conn.core.InternAtom(False, len(key), key).reply().atom,
            self._conn.core.InternAtom(False, len(type), type).reply().atom,
            0,
            256
        ).reply().value

    def get_name(self):
        try:
            return self.get_property('WM_NAME', 'STRING').to_string()
        except WindowError:
            # This may happen if we try to query a window that has been destroyed
            log.exception('Error in `configure` method')
            return ''

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
        try:
            self._conn.core.ConfigureWindow(self._wid, mask, values, True).check()
        except WindowError:
            log.exception('Error in `configure` method')

    def map(self):
        if not self._mapped:
            log.debug('Mapping window %d', self._wid)
            try:
                self._conn.core.MapWindow(self._wid, True).check()
            except Exception:
                log.exception('Error in `map` method')
            self._mapped = True

    def unmap(self):
        if self._mapped:
            log.debug('Unmapping window %d', self._wid)
            try:
                self._conn.core.UnmapWindow(self._wid, True).check()
            except Exception:
                log.exception('Error in `unmap` method')
            self._mapped = False

    def grab_key(self, keysym, modifiers, owner_events=True, pointer_mode=GrabMode.Async, keyboard_mode=GrabMode.Async):
        code = self._wm.get_keymap().keysym_to_keycode(keysym)
        self._conn.core.GrabKey(1 if owner_events else 0, self._wid, modifiers, code, pointer_mode, keyboard_mode, True)

    def grab_button(self, button, modifiers, owner_events, event_mask, pointer_mode=GrabMode.Async, keyboard_mode=GrabMode.Async):
        self._conn.core.GrabButton(
            1 if owner_events else 0,
            self._wid,
            event_mask,
            pointer_mode,
            keyboard_mode,
            Atom._None,
            Atom._None,
            button,
            modifiers
        )

    def ungrab_button(self, button=Atom.Any, modifiers=ModMask.Any):
        self._conn.core.UngrabButton(button, self._wid, modifiers)

    def get_page(self):
        return self._page

    def focus(self):
        # PointerRoot
        log.debug('Focusing window %s', self)
        # self.conn.core.SetInputFocus(InputFocus.PointerRoot, self.wid, Time.CurrentTime)
        # if self.page.current_window is not None:
        #     self.page.current_window.ungrab_button()
        # for window in self.page.get_windows():
        #     window.ungrab_button()
        # self.grab_button(Atom.Any, ModMask.Any, True, EventMask.ButtonPress | EventMask.ButtonRelease | EventMask.ButtonMotion)
        # self.unmap()
        # self.map()
        try:
            self._conn.core.SetInputFocus(InputFocus.PointerRoot, self._wid, Time.CurrentTime, True).check()
            bus.fire('window:focus', self)
        except:
            log.exception('Failed to focus window')

    def __repr__(self):
        return '<Window id={} page={}>'.format(
            self._wid,
            self._page.get_name()
        )

    __str__ = __repr__

    # def register_key(self, keysym, modifiers, callback):

    # def destroy(self):
    #     self.conn.core.DestroyWindow(self.wid)

    def expose(self):
        pass

    def get_wid(self):
        return self._wid

    get_id = get_wid


class RootWindow(Window):
    def __init__(self, *args, **kwargs):
        self._wallpaper = kwargs.pop('wallpaper')

        super(RootWindow, self).__init__(*args, **kwargs)

        screen = self._wm.get_screen()

        # self._painter = CairoPainter(self._wm, self._wid, screen.width_in_pixels, screen.height_in_pixels)
        # self._painter.load_png_surface(self._wallpaper)

    def __repr__(self):
        return '<RootWindow id={}>'.format(
            self._wid
        )

    __str__ = __repr__

    # def expose(self):
    #     print('Exposing root')

    #     # painter = Painter(self.wm, self.wid)

    #     # painter.move_to(100, 100)
    #     # painter.set_font('DejaVu Sans Mono', 32)
    #     # painter.draw_text('Foobar')

    #     # painter.render()

    #     # # painter.poly(
    #     # #     [0, 0],
    #     # #     [100, 100],
    #     # #     [300, 200],
    #     # #     [400, 400]
    #     # # )

    #     # # pid = self.conn.generate_id()
    #     # # self.conn.core.CreatePixmap(self.wm.get_screen().root_depth, pid, self.wid, screen.width_in_pixels, screen.height_in_pixels, True).check()

    #     # self.conn.core.ChangeWindowAttributes(self.wid, CW.BackPixmap, [
    #     #     painter.pixmap_id
    #     #     # pid
    #     # ], True).check()

    #     # self.painter.set_color(0x225588)
    #     # self.painter.fill()

    #     self.painter.render()
