from xcffib.xproto import GC, CoordMode, POINT, RECTANGLE
import cairocffi


ALPHABET = ''.join(list(map(chr, range(33, 126))))


# class Painter(object):
#     def __init__(self, wm, drawable):
#         self._wm = wm
#         self._conn = wm.get_conn()
#         self._screen = wm.get_screen()

#         self._drawable = drawable

#         self._gcid = self._conn.generate_id()
#         self._conn.core.CreateGC(
#             self._gcid,
#             drawable,
#             GC.Foreground | GC.Background,
#             [self._screen.white_pixel, self._screen.black_pixel],
#             True
#         ).check()

#         self._name_fid_map = {}
#         self._current_font = None

#     def change(self, fontname=None, fg=None, bg=None):
#         flags = 0
#         values = []

#         if fg is not None:
#             flags |= GC.Foreground
#             values.append(fg)

#         if bg is not None:
#             flags |= GC.Background
#             values.append(bg)

#         if fontname is not None:
#             if fontname not in self._name_fid_map:
#                 fid = self._conn.generate_id()
#                 self._conn.core.OpenFont(fid, len(fontname), fontname)
#             else:
#                 fid = self._name_fid_map[fontname]
#             flags |= GC.Font
#             values.append(fid)

#         self._conn.core.ChangeGC(
#             self._gcid,
#             flags,
#             values
#         )

#     def poly(self, *args):
#         self._conn.core.PolyPoint(
#             CoordMode.Origin,
#             self._drawable,
#             self._gcid,
#             len(args),
#             list(map(lambda coords: POINT.synthetic(*coords), args)),
#             True
#         ).check()

#     def text(self, x, y, string):
#         self._conn.core.ImageText8(len(string), self._drawable, self._gcid, x, y, string, True).check()

#     def rect(self, x, y, width, height):
#         self._conn.core.PolyFillRectangle(self._drawable, self._gcid, 1, [RECTANGLE.synthetic(x, y, width, height)], True)


# class CairoPainter(Painter):
#     def __init__(self, wm, drawable, width, height):
#         super(CairoPainter, self).__init__(wm, drawable)

#         self._width = width
#         self._height = height

#         self._pixmap_id = self._conn.generate_id()
#         self._conn.core.CreatePixmap(
#             self._screen.root_depth,
#             self._pixmap_id,
#             self._drawable,
#             width,
#             height,
#             True
#         ).check()

#         max_depth = [depth for depth in self._screen.allowed_depths if depth.depth == self._screen.root_depth][0]
#         assert max_depth.depth == 24
#         # print(len(max_depth.visuals))
#         # for visual in max_depth.visuals:
#         #     # print(visual.bits_per_rgb_value, visual.red_mask, visual.green_mask, visual.blue_mask)
#         #     print(visual.bufsize, visual.visual_id)
#         # assert len(max_depth.visuals) == 1

#         # for d in self.screen.allowed_depths:
#         #     print(d.depth, d.visuals)

#         self._surface = cairocffi.XCBSurface(
#             self._conn,
#             self._pixmap_id,
#             max_depth.visuals[0],
#             width,
#             height
#         )

#         self._ctx = cairocffi.Context(self._surface)

#     def render(self):
#         self._conn.core.CopyArea(
#             self._pixmap_id,
#             self._drawable,
#             self._gcid,
#             0, 0, 0, 0,
#             self._width,
#             self._height,
#             True
#         ).check()

#     def draw_text(self, string):
#         _, _, w, h, xa, ya = self._ctx.text_extents(string)
#         xb, yb = self._text_extents[0:2]

#         x, y = self._ctx.get_current_point()

#         x2 = x - xb
#         y2 = y - yb

#         self._ctx.move_to(x2, y2)
#         self._ctx.show_text(string)
#         self._ctx.move_to(x + xa, y + ya)

#         return xa, ya

#         # return x + xa, y

#     def color_to_rgb(self, color):
#         return [float(component) / 255 for component in (
#             (color >> 16) & 0xFF,
#             (color >> 8) & 0xFF,
#             color & 0xFF
#         )]

#     def move_to(self, x, y, abs=False):
#         (self._ctx.rel_move_to if abs else self._ctx.move_to)(x, y)

#     def set_color(self, color):
#         self._ctx.set_source_rgb(*self.color_to_rgb(color))

#     def fill(self):
#         self._ctx.set_operator(cairocffi.OPERATOR_SOURCE)
#         self._ctx.paint()

#     def set_font(self, family=None, size=None, bold=None):
#         font_face_args = {}
#         if family is not None:
#             font_face_args['family'] = family
#         if bold is not None:
#             font_face_args['weight'] = cairocffi.FONT_WEIGHT_BOLD if bold else cairocffi.FONT_WEIGHT_NORMAL
#         if len(font_face_args.keys()):
#             self._ctx.select_font_face(**font_face_args)
#             self._text_extents = self._ctx.text_extents(ALPHABET)
#         if size is not None:
#             self._ctx.set_font_size(size)

#     def load_png_surface(self, path):
#         surface = cairocffi.ImageSurface.create_from_png(path)
#         self._ctx.set_source_surface(surface)
#         self._ctx.paint()

#     def get_current_point(self):
#         if self._ctx.has_current_point():
#             return self._ctx.get_current_point()
#         return (0, 0)


class DrawableSurface(object):
    def __init__(self, wm, width, height):
        # self._surface = surface
        # self._ctx = cairocffi.Context(self._surface)
        # cairocffi.XCBSurface()
        self._wid = wm.get_root_win().get_wid()
        self._conn = wm.get_conn()

        screen = wm.get_screen()

        root_depth = screen.root_depth

        max_depth = [depth for depth in screen.allowed_depths if depth.depth == screen.root_depth][0]
        assert max_depth.depth == 24

        self._gcid = self._conn.generate_id()
        self._conn.core.CreateGC(
            self._gcid,
            self._wid,
            GC.Foreground | GC.Background,
            [screen.white_pixel, screen.black_pixel],
            True
        ).check()

        self._pixmap_id = self._conn.generate_id()
        self._conn.core.CreatePixmap(
            root_depth,
            self._pixmap_id,
            self._wid,
            width,
            height,
            True
        ).check()

        self._surface = cairocffi.XCBSurface(
            self._conn,
            self._pixmap_id,
            max_depth.visuals[0],
            width,
            height
        )

        self._ctx = cairocffi.Context(self._surface)

        self.set_font('DejaVu Sans Mono', 12, True)

    def get_pixmap_id(self):
        return self._pixmap_id

    def get_context(self):
        return self._ctx

    def copy(self, dst_wid, w, h, dst_x, dst_y):
        self._conn.core.CopyArea(
            self._pixmap_id,
            dst_wid,
            self._gcid,
            0, 0, dst_x, dst_y,
            w,
            h,
            True
        ).check()

    def draw_text(self, string):
        _, _, w, h, xa, ya = self._ctx.text_extents(string)
        xb, yb = self._text_extents[0:2]

        x, y = self._ctx.get_current_point()

        x2 = x - xb
        y2 = y - yb

        self._ctx.move_to(x2, y2)
        self._ctx.show_text(string)
        self._ctx.move_to(x + xa, y + ya)

        return xa, ya

    def color_to_rgb(self, color):
        return [float(component) / 255 for component in (
            (color >> 16) & 0xFF,
            (color >> 8) & 0xFF,
            color & 0xFF
        )]

    def move_to(self, x, y, abs=False):
        (self._ctx.rel_move_to if abs else self._ctx.move_to)(x, y)

    def set_color(self, color):
        self._ctx.set_source_rgb(*self.color_to_rgb(color))

    def fill(self):
        self._ctx.set_operator(cairocffi.OPERATOR_SOURCE)
        self._ctx.paint()

    def set_font(self, family=None, size=None, bold=None):
        font_face_args = {}
        if family is not None:
            font_face_args['family'] = family
        if bold is not None:
            font_face_args['weight'] = cairocffi.FONT_WEIGHT_BOLD if bold else cairocffi.FONT_WEIGHT_NORMAL
        if len(font_face_args.keys()):
            self._ctx.select_font_face(**font_face_args)
            self._text_extents = self._ctx.text_extents(ALPHABET)
        if size is not None:
            self._ctx.set_font_size(size)

    # def load_png_surface(self, path):
    #     surface = cairocffi.ImageSurface.create_from_png(path)
    #     self._ctx.set_source_surface(surface)
    #     self._ctx.paint()

    def get_current_point(self):
        if self._ctx.has_current_point():
            return self._ctx.get_current_point()
        return (0, 0)

    def reset(self):
        self._ctx.move_to(0, 0)
