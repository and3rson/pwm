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
