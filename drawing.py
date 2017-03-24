from xcffib.xproto import GC, CoordMode, RECTANGLE
import cairocffi


class Painter(object):
    def __init__(self, wm, drawable):
        self.wm = wm
        self.conn = wm.get_conn()
        self.screen = wm.get_screen()

        self.drawable = drawable

        self.gcid = self.conn.generate_id()
        self.conn.core.CreateGC(
            self.gcid,
            drawable,
            GC.Foreground | GC.Background,
            [self.screen.white_pixel, self.screen.black_pixel],
            True
        ).check()

        self.name_fid_map = {}
        self.current_font = None

    def change(self, fontname=None, fg=None, bg=None):
        flags = 0
        values = []

        if fg is not None:
            flags |= GC.Foreground
            values.append(fg)

        if bg is not None:
            flags |= GC.Background
            values.append(bg)

        if fontname is not None:
            if fontname not in self.name_fid_map:
                fid = self.conn.generate_id()
                self.conn.core.OpenFont(fid, len(fontname), fontname)
            else:
                fid = self.name_fid_map[fontname]
            flags |= GC.Font
            values.append(fid)

        self.conn.core.ChangeGC(
            self.gcid,
            flags,
            values
        )

    def poly(self, *args):
        self.conn.core.PolyPoint(
            CoordMode.Origin,
            self.drawable,
            self.gcid,
            len(args),
            args,
            True
        ).check()

    def text(self, x, y, string):
        self.conn.core.ImageText8(len(string), self.drawable, self.gcid, x, y, string, True).check()

    def rect(self, x, y, width, height):
        self.conn.core.PolyFillRectangle(self.drawable, self.gcid, 1, [RECTANGLE.synthetic(x, y, width, height)], True)


class CairoPainter(Painter):
    def __init__(self, wm, drawable, width, height):
        super(CairoPainter, self).__init__(wm, drawable)

        self.width = width
        self.height = height

        self.pixmap_id = self.conn.generate_id()
        self.conn.core.CreatePixmap(
            self.screen.root_depth,
            self.pixmap_id,
            self.drawable,
            width,
            height,
            True
        ).check()

        max_depth = [depth for depth in self.screen.allowed_depths if depth.depth == self.screen.root_depth][0]
        assert max_depth.depth == 24
        # print(len(max_depth.visuals))
        # for visual in max_depth.visuals:
        #     # print(visual.bits_per_rgb_value, visual.red_mask, visual.green_mask, visual.blue_mask)
        #     print(visual.bufsize, visual.visual_id)
        # assert len(max_depth.visuals) == 1

        # for d in self.screen.allowed_depths:
        #     print(d.depth, d.visuals)

        self.surface = cairocffi.XCBSurface(
            self.conn,
            self.pixmap_id,
            max_depth.visuals[0],
            width,
            height
        )

        self.ctx = cairocffi.Context(self.surface)

    def render(self):
        self.conn.core.CopyArea(
            self.pixmap_id,
            self.drawable,
            self.gcid,
            0, 0, 0, 0,
            self.width,
            self.height,
            True
        ).check()

    def draw_text(self, string):
        xb, yb, w, h, xa, ya = self.ctx.text_extents(string)

        x, y = self.ctx.get_current_point()

        x2 = x - xb
        y2 = y - yb

        self.ctx.move_to(x2, y2)
        self.ctx.show_text(string)
        self.ctx.move_to(x + xa, y + ya)
        # return x + xa, y

    def color_to_rgb(self, color):
        return [float(component) / 255 for component in (
            (color >> 16) & 0xFF,
            (color >> 8) & 0xFF,
            color & 0xFF
        )]

    def move_to(self, x, y, abs=False):
        (self.ctx.rel_move_to if abs else self.ctx.move_to)(x, y)

    def set_color(self, color):
        print(self.color_to_rgb(color))
        self.ctx.set_source_rgb(*self.color_to_rgb(color))

    def fill(self):
        self.ctx.set_operator(cairocffi.OPERATOR_SOURCE)
        self.ctx.paint()

    def set_font(self, family=None, size=None):
        if family is not None:
            self.ctx.select_font_face(family=family)
        if size is not None:
            self.ctx.set_font_size(size)
