import layout
from bus import bus


class Page(object):
    def __init__(self, wm, name, layout_name):
        self._wm = wm
        self._name = name
        self._windows = []
        layout_cls = layout.get_layout_by_name(layout_name)
        self._layout = layout_cls(wm, self)
        self._current_window = None

    def get_name(self):
        return self._name

    def get_window(self, wid):
        return next(iter([
            window
            for window
            in self._windows
            if window.wid == wid
        ]), None)

    def get_windows(self):
        return self._windows

    def get_layout(self):
        return self._layout

    def add_window(self, window):
        self._windows.append(window)
        self._layout.lay_out()
        if self._current_window is None:
            self._current_window = window
        # print('focus')
        # window.focus()

    def remove_window(self, window):
        # if self.current_window == window:
        #     if len(self.windows):
        #         self.current_window = self.windows[0]
        #         self.current_window.focus()
        #     else:
        #         self.current_window = None
        self._windows.remove(window)
        if window == self._current_window:
            self._current_window = self._windows[0] if len(self._windows) else None
        self._layout.lay_out()

    def focus_window(self, window):
        self._current_window = window
        self._layout.focus_window(window)
        # window.focus()

    def show(self):
        self._layout.show()
        if self._current_window is not None:
            self._current_window.focus()
        self._layout.lay_out()

        # print('show')
        bus.fire('page:show', self)

    def hide(self):
        self._layout.hide()

        bus.fire('page:hide', self)

    def get_current_window(self):
        # TODO: Implement this!
        return self._current_window

    def __repr__(self):
        return '<Page name={} windows={}, layout={}>'.format(
            self._name,
            len(self._windows),
            self._layout.get_name()
        )

    __str__ = __repr__
