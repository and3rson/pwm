class Layout(object):
    def __init__(self, wm, page):
        self._wm = wm
        self._page = page

    @classmethod
    def get_name(cls):
        if not getattr(cls, 'name', None):
            raise NotImplementedError('Layout is missing "name" property (or it is None.)')
        return cls.name

    def lay_out(self):
        raise NotImplementedError()

    def show(self):
        for window in self._page.get_windows():
            # log.debug('Mapping %d', window.wid)
            window.map()

    def hide(self):
        for window in self._page.get_windows():
            # log.debug('Unmapping %d', window.wid)
            window.unmap()

    def focus_window(self, window):
        raise NotImplementedError()

    def __repr__(self):
        return '<Layout name={}>'.format(
            self._name
        )

    __str__ = __repr__


class HTile(Layout):
    name = 'htile'

    def lay_out(self):
        x, y, w, h = self._wm.get_usable_space()
        windows = self._page.get_windows()
        count = len(windows)
        if not count:
            return
        win_width = int(w / count)
        win_height = h

        for i, window in enumerate(windows):
            window.configure(x=x + win_width * i, y=y, width=win_width, height=win_height)

    def focus_window(self, window):
        window.focus()


class Max(Layout):
    name = 'max'

    def lay_out(self):
        x, y, w, h = self._wm.get_usable_space()
        for window in self._page.get_windows():
            # print('Lay out', window, dict(x=x + win_width * i, y=y, width=win_width, height=win_height))
            # print('Layout', window)
            if window == self._page.get_current_window():
                window.map()
                window.configure(
                    x=x,
                    y=y,
                    width=w,
                    height=h
                )
            else:
                window.unmap()

    def focus_window(self, window):
        # print('focus')
        # for other_window in self.page.get_windows():
        #     if other_window == window:
        #         other_window.map()
        #     else:
        #         other_window.unmap()
        self.lay_out()
        window.focus()


layout_map = {}
name = None
value = None
for name, value in vars().items():
    if isinstance(value, type) and value != Layout and issubclass(value, Layout):
        layout_map[value.name] = value


def get_layout_by_name(name):
    return layout_map[name]
