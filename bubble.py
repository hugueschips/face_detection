import cv2
import numpy as np

class Bubble:
    def __init__(self, img, pt1, pt2, text, bg_color, font_face, scale, thickness, margin):
        if not text: return None
        self.img = img
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
        x2 = x1 + txt_size[0][0] + 2*self.margin
        y2 = y1 - n_lines * self.dy - 2*self.margin
        return (x2, y2)

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

    def uncrop(self):
        h, l, d = self.img.shape
        p4 = self.triangle[1,0,:]
        p4_not_in_img = (p4[0] > l-4*self.margin) or (p4[1] > h-4*self.margin)
        if p4_not_in_img:
            self.text = None
            return None
        upper_right_corner_not_in_img = (self.p2[0]>l) or (self.p2[1]<5)
        for i in range(25):
            if not upper_right_corner_not_in_img:
                break
            self.scale *= .9
            self.margin = int(self.margin * .9)
            self.p2 = self.get_p2()
            self.triangle = self.get_triangle()
            self.x_text = self.p1[0] + self.margin
            self.y_text = self.p2[1] + self.dy + self.margin
            upper_right_corner_not_in_img = (self.p2[0]>l) or (self.p2[1]<5)
        if upper_right_corner_not_in_img:
            self.text = None
            return None

    def draw(self, img):
        if self.text:
            cv2.rectangle(img, self.p1, self.p2, (255, 255, 255), cv2.FILLED)
            cv2.rectangle(img, self.p1, self.p2, (0, 0, 0), self.thickness)
            cv2.fillConvexPoly(img, self.triangle, (0, 0, 0), self.thickness)
            for line in self.text:
                color = (0,0,0) #text_color(line)
                cv2.putText(img, line, (self.x_text, self.y_text), self.font_face, self.scale, color, 1, cv2.LINE_AA)
                self.get_new_line_y()

    def check_text_is_inside(self):
        assert self.x_text > self.p1[0]
        assert self.y_text > self.p2[1]
        if self.y_text <= self.p2[1]:
            print(f'p2 y is {{self.p2[1]}} and text y is {{self.y_text}}')
