import window
import drawing
from xcffib.xproto import CW, WindowClass, EventMask  # , POINT
import cairocffi
from bus import bus


class Panel(window.Window):
    def __init__(self, wm, x, y, width, height):
        self.wm = wm
        self.conn = wm.get_conn()

        wid = self.conn.generate_id()

        root_wid = wm.get_root_win().wid
        screen = wm.get_screen()

        self.conn.core.CreateWindow(
            screen.root_depth,
            wid, root_wid,
            x, y, width, height,
            0,
            WindowClass.InputOutput,
            screen.root_visual,
            CW.BorderPixel,  # | CW.EventMask,
            [screen.white_pixel],  # , EventMask.Exposure],
            True
        ).check()

        super(Panel, self).__init__(wm, wid, None)

        self.map()

        self.painter = drawing.CairoPainter(wm, wid, width, height)

        self.update()

        bus.on('page:show', self.update)
        bus.on('window:focus', self.update)
        bus.on('window:register', self.update)
        bus.on('window:unregister', self.update)

    def update(self, *args):
        # ctx.set_source_rgb(1, 0, 0)
        # ctx.move_to(10, 10)
        # ctx.rel_line_to(15, 15)
        # ctx.stroke()

        self.painter.set_color(0x111111)
        self.painter.fill()

        pages = [('{}' if page != self.wm.current_page else '[{}]').format(page.name) for page in self.wm.pages]
        page = self.wm.current_page
        windows = [('{}' if window != page.current_window else '[{}]').format(window.get_name()) for window in page.get_windows()]

        self.painter.set_font('DejaVu Sans Mono', 12)

        self.painter.move_to(6, 6)
        self.painter.set_color(0x0055FF)
        self.painter.draw_text(' '.join(pages))
        self.painter.move_to(12, 0, True)
        self.painter.set_color(0x00FF55)
        self.painter.draw_text(' '.join(windows))
        # ctx.show_text(' '.join(pages) + ' | ' + ' '.join(windows))

        # ext = ctx.text_extents('foobar')
        # # xb, yb, w, h, xa, ya
        # print(ext)
        # # import ipdb; ipdb.set_trace()

        # ctx.move_to(200, 6)
        # ctx.set_source_rgb(1.0, 0, 0)
        # self.painter.draw_text('Foo')
        # ctx.set_source_rgb(0, 1.0, 0)
        # self.painter.draw_text('Bar')
        # ctx.set_source_rgb(0, 0, 1.0)
        # self.painter.draw_text('Baz')

        # ctx.show_text(' '.join(pages) + ' | ' + ' '.join(windows))

        # ext = ctx.text_extents('foobar')
        # print(ext)
        # import ipdb; ipdb.set_trace()

        self.painter.render()

        # self.painter.change(fg=0x222222, bg=0x222222)

        # self.painter.rect(0, 0, screen.width_in_pixels, screen.height_in_pixels)

        # self.painter.change(fg=0x00FFFF, fontname='*x20')

        # # self.painter.poly(POINT.synthetic(10, 10), POINT.synthetic(30, 10))

        # self.painter.text(4, 18, 'PWM')
