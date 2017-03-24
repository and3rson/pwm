class Layout(object):
    def __init__(self, wm, page):
        self.wm = wm
        self.page = page

    @classmethod
    def get_name(cls):
        if not getattr(cls, 'name', None):
            raise NotImplementedError('Layout is missing "name" property (or it is None.)')
        return cls.name

    def lay_out(self):
        raise NotImplementedError()

    def show(self):
        for window in self.page.get_windows():
            print('Mapping', window.wid)
            window.map()

    def hide(self):
        for window in self.page.get_windows():
            print('Unmapping', window.wid)
            window.unmap()

    def __repr__(self):
        return '<Layout name={}>'.format(
            self.name
        )

    __str__ = __repr__


class HTile(Layout):
    name = 'htile'

    def lay_out(self):
        screen = self.wm.get_screen()
        windows = self.page.get_windows()
        count = len(windows)
        if not count:
            return
        win_width = int(screen.width_in_pixels / count)
        win_height = screen.height_in_pixels

        for i, window in enumerate(windows):
            window.configure(x=win_width * i, y=24, width=win_width, height=win_height)


class Max(Layout):
    name = 'max'

    def lay_out(self):
        screen = self.wm.get_screen()
        for window in self.page.get_windows():
            if window == self.page.get_current_window():
                window.map()
                window.configure(
                    x=0,
                    y=24,
                    width=screen.width_in_pixels,
                    height=screen.height_in_pixels
                )
            else:
                window.unmap()


layout_map = {}
name = None
value = None
for name, value in vars().items():
    if isinstance(value, type) and value != Layout and issubclass(value, Layout):
        layout_map[value.name] = value


def get_layout_by_name(name):
    return layout_map[name]
