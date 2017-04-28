from window import Window
import drawing
from xcffib.xproto import CW, WindowClass
from bus import bus
import datetime
import cairocffi


class Panel(Window):
    def __init__(self, wm, position, height):
        self._wm = wm
        self._conn = wm.get_conn()

        self._position = position
        self._height = height

        self._widgets = []

        wid = self._conn.generate_id()

        root_wid = wm.get_root_win().get_wid()
        screen = wm.get_screen()

        x = 0
        y = 0 if position == 'top' else (screen.height_in_pixels - height)
        w = screen.width_in_pixels
        h = height

        self._width = w

        self._conn.core.CreateWindow(
            screen.root_depth,
            wid, root_wid,
            x, y, w, h,
            0,
            WindowClass.InputOutput,
            screen.root_visual,
            CW.BorderPixel,  # | CW.EventMask,
            [screen.white_pixel],  # , EventMask.Exposure],
            True
        ).check()

        # self._pixmap_id = self._conn.generate_id()
        # self._conn.core.CreatePixmap(
        #     screen.root_depth,
        #     self._pixmap_id,
        #     wid,
        #     w,
        #     height,
        #     True
        # ).check()

        self._painter = drawing.DrawableSurface(self._wm, self.get_width(), self.get_height())

        # max_depth = [depth for depth in screen.allowed_depths if depth.depth == screen.root_depth][0]
        # assert max_depth.depth == 24

        # self._surface = cairocffi.XCBSurface(
        #     self._conn,
        #     self._pixmap_id,
        #     max_depth.visuals[0],
        #     w,
        #     height
        # )

        # self._ctx = cairocffi.Context(self._surface)

        super(Panel, self).__init__(wm, wid, None)

        self.set_property('_NET_WM_NAME', 'UTF8_STRING', 'Panel')

        self.map()

        # self._painter = drawing.CairoPainter(wm, wid, w, h)

        # self._painter.set_font('DejaVu Sans Mono', 12, True)

        bus.on('page:show', self.expose)
        bus.on('window:focus', self.expose)
        bus.on('window:register', self.expose)
        bus.on('window:unregister', self.expose)

    def get_position(self):
        return self._position

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def expose(self, *args):
        # print('       Exposing!!!!!!!!')
        self._painter.set_color(0xFF1177)
        self._painter.fill()
        # self._painter.copy(
        #     self._pixmap_id,
        #     self.get_width(),
        #     self.get_height(),
        #     0,
        #     0
        # )

        # self._painter.set_font('DejaVu Sans Mono', 12, True)

        # offset = 6

        widths = []

        for widget in self._widgets:
            widths.append(widget._render())

        expanding_count = len(list(filter(lambda width: width <= 0, widths)))
        static_widths = sum(list(filter(lambda width: width > 0, widths)))

        free_for_expanding = self.get_width() - static_widths

        widths = map(lambda width: (free_for_expanding / expanding_count) if width <= 0 else width, widths)

        offset_x = 0

        for widget, width in zip(self._widgets, widths):
            print('Widget =', widget, 'width =', width, 'offset =', offset_x)
            # self._surface.set_source_surface(widget.get_surface(), offset_x, 0)
            # self._surface.rectangle(offset_x, 0, width, self.get_height())
            # self._surface.fill()
            widget.get_painter().copy(
                self._painter.get_pixmap_id(),
                int(width),
                self.get_height(),
                int(offset_x),
                0
            )
            # widget.get_painter().copy(
            #     self._wid,
            #     int(width),
            #     self.get_height(),
            #     int(offset_x),
            #     0
            # )

            offset_x += width

        self._painter.copy(
            self._wid,
            self.get_width(),
            self.get_height(),
            0,
            0
        )

        # self._conn.core.CopyArea(
        #     self._painter.get_pixmap_id(),
        #     self._wid,
        #     self._gcid,
        #     0, 0, 0, 0,
        #     self.get_width(),
        #     self.get_height(),
        #     True
        # ).check()

    def add_widget(self, widget_cls, args):
        widget = widget_cls(self._wm, self)
        widget.init(*args)
        self._widgets.append(widget)


class Widget(object):
    def __init__(self, wm, panel):
        self._wm = wm
        self._panel = panel
        # self._surface = cairocffi.ImageSurface(cairocffi.FORMAT_ARGB32, panel.get_width(), panel.get_height())
        # self._ctx = cairocffi.Context(self._surface)
        # self._painter = drawing.SurfacePainter(self._surface)
        self._painter = drawing.DrawableSurface(
            wm,
            panel.get_width(),
            panel.get_height()
        )
        # self._painter = self._drawable_surface.get_painter()

    def init(self):
        pass

    def _render(self):
        self._painter.set_color(0x111111)
        self._painter.fill()
        self._painter.reset()
        self._surface_width = self.render(self._wm, self._painter)
        return self._surface_width
        # self._ctx.set_operator(cairocffi.OPERATOR_SOURCE)
        # self._ctx.paint()
        # self._rendered_width = self.render(self._painter)

    def get_painter(self):
        return self._painter


class PagesWidget(Widget):
    def render(self, wm, painter):
        width = 0

        page_iter = iter(wm.get_pages())
        next(page_iter, None)

        for page in wm.get_pages():
            if page == wm.get_current_page():
                painter.set_color(0x0055FF)
            else:
                painter.set_color(0xFFFFFF)
            width += painter.draw_text(page.get_name() + (' ' if next(page_iter, None) else ''))[0]

        return width


class SepWidget(Widget):
    def init(self, width):
        self._width = width

    def render(self, wm, painter):
        return self._width


class WindowsWidget(Widget):
    def render(self, wm, painter):
        width = 0

        window_iter = iter(wm.get_current_page().get_windows())
        next(window_iter, None)

        for window in wm.get_current_page().get_windows():
            if window == wm.get_current_page().get_current_window():
                painter.set_color(0x0055FF)
            else:
                painter.set_color(0xFFFFFF)
            width += painter.draw_text(window.get_name() + (' ' if next(window_iter, None) else ''))[0]

        return -1


class ClockWidget(Widget):
    def render(self, wm, painter):
        painter.set_color(0x0055FF)
        size = painter.draw_text(datetime.datetime.now().strftime('%H:%M:%S'))

        return size[0]
