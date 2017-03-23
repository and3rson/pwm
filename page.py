import layout


class Page(object):
    def __init__(self, wm, name, layout_name):
        self.wm = wm
        self.name = name
        self.windows = []
        layout_cls = layout.get_layout_by_name(layout_name)
        self.layout = layout_cls(wm, self)

    def get_window(self, wid):
        return next(iter([
            window
            for window
            in self.windows
            if window.wid == wid
        ]), None)

    def get_windows(self):
        return self.windows

    def add_window(self, window):
        self.windows.append(window)
        self.layout.lay_out()

    def remove_window(self, window):
        self.windows.remove(window)
        self.layout.lay_out()

    def show(self):
        self.layout.show()
        self.layout.lay_out()

    def hide(self):
        self.layout.hide()

    def get_current_window(self):
        # TODO: Implement this!
        return self.windows[0]

    def __repr__(self):
        return '<Page name={} windows={}, layout={}>'.format(
            self.name,
            len(self.windows),
            self.layout.name
        )

    __str__ = __repr__
