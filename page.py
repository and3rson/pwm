import layout
from bus import bus


class Page(object):
    def __init__(self, wm, name, layout_name):
        self.wm = wm
        self.name = name
        self.windows = []
        layout_cls = layout.get_layout_by_name(layout_name)
        self.layout = layout_cls(wm, self)
        self.current_window = None

    def get_name(self):
        return self.name

    def get_window(self, wid):
        return next(iter([
            window
            for window
            in self.windows
            if window.wid == wid
        ]), None)

    def get_windows(self):
        return self.windows

    def get_layout(self):
        return self.layout

    def add_window(self, window):
        self.windows.append(window)
        self.layout.lay_out()
        if self.current_window is None:
            self.current_window = window
        # print('focus')
        # window.focus()

    def remove_window(self, window):
        # if self.current_window == window:
        #     if len(self.windows):
        #         self.current_window = self.windows[0]
        #         self.current_window.focus()
        #     else:
        #         self.current_window = None
        self.windows.remove(window)
        if window == self.current_window:
            self.current_window = self.windows[0] if len(self.windows) else None
        self.layout.lay_out()

    def focus_window(self, window):
        self.current_window = window
        window.focus()

    def show(self):
        self.layout.show()
        if self.current_window is not None:
            self.current_window.focus()
        self.layout.lay_out()

        bus.fire('page:show', self)

    def hide(self):
        self.layout.hide()

        bus.fire('page:hide', self)

    def get_current_window(self):
        # TODO: Implement this!
        return self.current_window

    def __repr__(self):
        return '<Page name={} windows={}, layout={}>'.format(
            self.name,
            len(self.windows),
            self.layout.name
        )

    __str__ = __repr__
