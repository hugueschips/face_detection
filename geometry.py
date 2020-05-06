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

    def shift_right(self, x):
        if (self.a.x + x >= 0) and (self.c.x + x <= self.xdim):
            self.a.x += x
            self.c.x += x
        return self

    def shift_down(self, y):
        if (self.a.y + y >= 0) and (self.c.y + y <= self.ydim):
            self.a.y += y
            self.c.y += y
        return self

    def center(self):
        return (self.a + self.c) // 2

    def x_diff(self, r):
        return (self.a.x - r.a.x)

    def y_diff(self, r):
        return (self.a.y - r.a.y)



