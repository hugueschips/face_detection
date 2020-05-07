import cv2
import numpy as np
from geometry import Point, Rectangle


class Bubble:
    """
             a ____________ b
              |            |
              |            |
              |            |
              |            |
              |____________|
        pt2. d   /          c
                /
               /
    pt1.      e

    """
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
        self.avoid_eyes()

    def get_shape(self):
        """
        computes ysize of a text line and shape of the rectangle
        """
        n_lines = len(self.text)
        longuest_line = max(self.text, key=len)
        txt_size = cv2.getTextSize(longuest_line, self.font_face, self.scale, self.thickness)
        self.dy = txt_size[0][1] + 3
        self.shape = (txt_size[0][0] + 2 * self.margin, n_lines * self.dy + 2 * self.margin)

    def get_ace(self):
        """
        computes positions of points named a, c and e as on sketch describing the class
        """
        d = Point(self.pt2.x + 4 * (self.pt2.x - self.pt1.x), self.pt2.y)
        self.a = Point(d.x, d.y - self.shape[1])
        self.c = Point(d.x + self.shape[0], d.y)
        self.e = Point(d.x, self.pt1.y)

    def text_start(self, i):
        """
        returns the point where ith text line should begin
        """
        return Point(self.a.x + self.margin, self.a.y + self.margin + (i + 1) * self.dy)

    def get_rectangle(self):
        self.rec = Rectangle(self.a, self.c, self.xdim, self.ydim)
        self.a = self.rec.a
        self.c = self.rec.c

    def update_ac(self):
        """
        to be executed after each rectangle shift
        """
        if self.rec:
            self.a = self.rec.a
            self.c = self.rec.c

    def avoid_eyes(self):
        """
        shifts up bubble if it overlaps the eye.
        """
        if self.pt2.x - self.rec.a.x > -self.dy:
            self.rec.shift_down(-self.dy)
            self.a = self.rec.a
            self.c = self.rec.c


    def draw(self, img, color_dic):
        if self.text:
            ## Draw arrow
            center = (self.a + self.c) // 2
            center.x = self.c.x #max(center.x, self.e.x + self.dy)
            cv2.line(img, (self.e.x, self.e.y), (center.x, center.y), (0, 0, 0), self.thickness)
            ## Draw white rectangle
            cv2.rectangle(img, (self.a.x, self.a.y), (self.c.x, self.c.y), (255, 255, 255), cv2.FILLED)
            ## Draw black rectangle boarders
            cv2.rectangle(img, (self.a.x, self.a.y), (self.c.x, self.c.y), (0, 0, 0), self.thickness)
            ## Add text inside
            for i, line in enumerate(self.text):
                color = color_dic[line]
                p = self.text_start(i)
                cv2.putText(img, line, (p.x, p.y), self.font_face, self.scale, color, 1, cv2.LINE_AA)
