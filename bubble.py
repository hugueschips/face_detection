import cv2
import numpy as np
from geometry import Point, Rectangle


class Bubble:
    '''
             a ____________ b
              |            |
              |            |
              |            |
              |            |
              |____________|
             d   /          c
                /
               /
             e
         '''
    bg_color = (0, 255, 0)
    font_face = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 4
    margin = 20

    def __init__(self, img, pt1, pt2, text):
        self.ydim, self.xdim, nc = img.shape
        self.scale = 1 * self.xdim / 1280.
        self.margin = int(self.scale * self.margin)
        self.pt1 = pt1
        self.pt2 = pt2
        self.text = text
        self.get_shape()
        self.get_ace()
        self.get_rectangle()

    def get_shape(self):
        n_lines = len(self.text)
        longuest_line = max(self.text, key=len)
        txt_size = cv2.getTextSize(longuest_line, self.font_face, self.scale, self.thickness)
        self.dy = txt_size[0][1] + 3
        self.shape = (txt_size[0][0] + 2 * self.margin, n_lines * self.dy + 2 * self.margin)

    def get_ace(self):
        d = Point(self.pt2.x + 4 * (self.pt2.x - self.pt1.x), self.pt2.y)
        self.a = Point(d.x, d.y - self.shape[1])
        self.c = Point(d.x + self.shape[0], d.y)
        self.e = Point(d.x, self.pt1.y)

    def text_start(self, i):
        return Point(self.a.x + self.margin, self.a.y + self.margin + (i + 1) * self.dy)

    def get_rectangle(self):
        self.rec = Rectangle(self.a, self.c, self.xdim, self.ydim)
        self.a = self.rec.a
        self.c = self.rec.c

    def update_ac(self):
        if self.rec:
            self.a = self.rec.a
            self.c = self.rec.c

    def draw(self, img, color_dic):
        if self.text:
            center = (self.a + self.c) // 2
            cv2.line(img, (self.e.x, self.e.y), (center.x, center.y), (0, 0, 0), self.thickness)
            cv2.rectangle(img, (self.a.x, self.a.y), (self.c.x, self.c.y), (255, 255, 255), cv2.FILLED)
            cv2.rectangle(img, (self.a.x, self.a.y), (self.c.x, self.c.y), (0, 0, 0), self.thickness)
            for i, line in enumerate(self.text):
                color = color_dic[line]
                p = self.text_start(i)
                cv2.putText(img, line, (p.x, p.y), self.font_face, self.scale, color, 1, cv2.LINE_AA)














class Bubble_old:
    def __init__(self, img, pt1, pt2, text, bg_color, font_face, scale, thickness, margin):
        if not text: return None
        self.img = img
        self.ydim, self.xdim, n_channel = img.shape
        self.bg_color = bg_color
        self.font_face = font_face
        self.scale = scale
        self.thickness = thickness
        self.margin = margin
        self.pt1 = pt1
        self.pt2 = pt2
        self.text = text
        self.p1 = self.get_p1()
        self.p2 = self.get_p2()
        self.a = self.get_a()
        self.c = self.get_c()
        self.triangle = self.get_triangle()
        self.x_text = self.p1[0] + self.margin
        self.y_text = self.p2[1] + self.dy + self.margin

    def get_p1(self):
        return (self.pt2[0] + 4 * (self.pt2[0] - self.pt1[0]), self.pt2[1])

    def get_p2(self):
        n_lines = len(self.text)
        longuest_line = max(self.text, key=len)
        txt_size = cv2.getTextSize(longuest_line, self.font_face, self.scale, self.thickness)
        self.dy = txt_size[0][1] + 3
        x1 = self.p1[0]
        y1 = self.p1[1]
        x2 = x1 + txt_size[0][0] + 2 * self.margin
        y2 = y1 - n_lines * self.dy - 2 * self.margin
        return (x2, y2)

    def get_a(self):
        return Point(self.p1[0], self.p2[1])

    def get_c(self):
        return Point(self.p2[0], self.p1[1])

    def get_triangle(self):
        def get_coord_on_line(t, x, y):
            return int(t * y + (1 - t) * x)

        x1 = self.p1[0]
        y1 = self.p1[1]
        x2 = self.p2[0]
        y2 = self.p2[1]
        p3 = [get_coord_on_line(2. / 7., x1, x2), y1]
        p4 = [x1, self.pt1[1]]
        p5 = [get_coord_on_line(3. / 7., x1, x2), y1]
        triangle = np.array([p3, p4, p5], np.int32)
        triangle = triangle.reshape((-1, 1, 2))
        return triangle

    def get_new_line_y(self):
        self.y_text += self.dy

    def downsize(self):
        self.scale *= .9
        self.margin = int(self.margin * .9)
        self.p2 = self.get_p2()
        self.triangle = self.get_triangle()
        self.x_text = self.p1[0] + self.margin
        self.y_text = self.p2[1] + self.dy + self.margin

    def uncrop(self):
        h, l, d = self.img.shape
        p4 = self.triangle[1, 0, :]
        p4_not_in_img = (p4[0] > l - 4 * self.margin) or (p4[1] > h - 4 * self.margin)
        if p4_not_in_img:
            self.text = None
            return None
        upper_right_corner_not_in_img = (self.p2[0] > l) or (self.p2[1] < 5)
        for i in range(25):
            if not upper_right_corner_not_in_img:
                break
            self.downsize()
            upper_right_corner_not_in_img = (self.p2[0] > l) or (self.p2[1] < 5)
        if upper_right_corner_not_in_img:
            self.text = None
            return None

    def draw(self, img):
        if self.text:
            cv2.rectangle(img, self.p1, self.p2, (255, 255, 255), cv2.FILLED)
            cv2.rectangle(img, self.p1, self.p2, (0, 0, 0), self.thickness)
            cv2.fillConvexPoly(img, self.triangle, (0, 0, 0), self.thickness)
            for line in self.text:
                color = (0, 0, 0)  # text_color(line)
                color = (1.0, 0.4980392156862745, 0.054901960784313725)
                cv2.putText(img, line, (self.x_text, self.y_text), self.font_face, self.scale, color, 1, cv2.LINE_AA)
                self.get_new_line_y()

    def check_text_is_inside(self):
        assert self.x_text > self.p1[0]
        assert self.y_text > self.p2[1]
        if self.y_text <= self.p2[1]:
            print(f'p2 y is {{self.p2[1]}} and text y is {{self.y_text}}')
