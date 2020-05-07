class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return str((self.x, self.y))

    def __str__(self):
        return str((self.x, self.y))

    def __add__(self, p):
        return Point(self.x + p.x, self.y + p.y)

    def __sub__(self, p):
        return Point(self.x - p.x, self.y - p.y)

    def __floordiv__(self, n):
        return Point(self.x // n, self.y // n)

    def __eq__(self, p):
        return self.x == p.x and self.y == p.y


class Rectangle:
    '''
         a ____________ b
          |            |
          |            |
          |            |
          |            |
          |____________|
         d              c

     '''

    def __init__(self, a, c, xdim, ydim):
        """
        create a rectangle is contained in the image, whose shape in (ydim, xdim)
        """
        assert a.x < c.x
        assert a.y < c.y
        if a.x < 0:
            c.x -= a.x
            a.x = 0
        if a.y < 0:
            c.y -= a.y
            a.y = 0
        if c.x > xdim:
            a.x -= c.x - xdim
            c.x = xdim
        if c.y > ydim:
            a.y -= c.y - ydim
            c.y = ydim
        self.a = a
        self.c = c
        self.xdim = xdim
        self.ydim = ydim

    def __repr__(self):
        return str(self.a) + '\n      ' + str(self.c)

    def __str__(self):
        return str(self.a) + '\n      ' + str(self.c)

    def __eq__(self, r):
        return str(self) == str(r)

    def is_left_of(self, r):
        return self.c.x <= r.a.x

    def is_above(self, r):
        return self.c.y <= r.a.y

    def do_overlap(self, r):
        b = self.is_left_of(r) or r.is_left_of(self) or self.is_above(r) or r.is_above(self)
        return not b

    def min_overlap(self, r):
        """
        returns minimum overlapping between two rectangle, its coordinate (x or y), and which
        rectangle is above or left
        """
        dx = min(self.c.x, r.c.x) - max(self.a.x, r.a.x)
        dy = min(self.c.y, r.c.y) - max(self.a.y, r.a.y)
        if dx > 0 and dy > 0:
                if dx < dy:
                    return dx, 0, (1, -1)[self.a.x < r.a.x]
                else:
                    return dy, 1, (1, -1)[self.a.y < r.a.y]

    def shift_right(self, x):
        maxi = self.xdim - self.c.y
        mini = -self.a.x
        x = max(mini, x) if x<0 else min(maxi, x)
        if x != 0:
            self.a.x += x
            self.c.x += x
            return True
        return False

    def shift_down(self, y):
        ymaxi = self.ydim - self.c.y
        ymini = -self.a.y
        if y<0:
            y = max(ymini, y)
        else:
            y = min(ymaxi, y)
        if y !=0:
            self.a.y += y
            self.c.y += y
            return True
        return False

    def center(self):
        return (self.a + self.c) // 2

