import tools as tools
import collections

'''
An elliptic curve object along with the algorithms
    - for adding points
    - finding intersections line with Curve
Curve is an abstract class from which three different forms of curves inherit
'''
# Definition of a point - coordinate
Coord = collections.namedtuple("Coord", ["x", "y"])


class Curve(object):

    def __init__(self, a, b, q,order):
        pass

    def at(self, x, sbit):
        pass

    def add(self, P, Q):
        pass

    def is_valid(self, p):
        pass

    def double(self, P):
        pass

    def double_and_add(self, P, n):
        pass

    def inverse(self, P):
        pass


class Weierstrass(Curve):

    def __init__(self, a, b, q,order):
        """elliptic curve as: (y**2 = x**3 + a * x + b) mod q
        - a, b: params of curve formula
        - q: prime number
        """
        assert 0 < a and a < q and 0 < b and b < q
        assert (4 * (a ** 3) + 27 * (b ** 2)) % q != 0
        self.a = a
        self.b = b
        self.q = q
        self.order = order

    def at(self, x, sbit):
        """find coordinate of a point at x
                x is X coordinate of point
                sbit is the sign bit
        """
        assert x < self.q
        ysq = (x ** 3 + self.a * x + self.b) % self.q
        root = tools.mod_sqrt(ysq, self.q)
        if root == 0:
            print "no point at this x coordinate"
            return -1
        return Coord(x, root) if sbit is True else Coord(x, -root % self.q)

    def add(self, P, Q):
        '''
        Adding two points P+Q
        if P is 0,0 or 0,1
                then return Q
        if Q is 0,0 or 0,1
                then return P
        If P==Q
                then double P
        else
                solve linear equation between line and elliptic curve
        '''
        # print P ," and", Q
        if P.x == 0 and (P.y == 0 or P.y == 1):
            return Q
        elif Q.x == 0 and (Q.y == 0 or Q.y == 1):
            return P
        elif P.x == Q.x and P.y == Q.y:
            return self.double(P)
        else:
            inv = tools.inversemodp(Q.x - P.x, self.q)
            pente = ((Q.y - P.y) * inv) % self.q
            if (pente is 0 and (P.x - Q.x == 0)):
                # print "What to do!",P,Q
                return Coord(0, 1)
            else:
                x = (pow(pente, 2, self.q) - P.x - Q.x) % self.q
                y = (pente * (P.x - x) - P.y) % self.q
                # print "adding ",Coord(x,y),self.is_valid(Coord(x,y))
                return Coord(x, y)

    def is_valid(self, p):
        '''
        Returns True if point on Curve
        Returns False otherwise
        '''
        if p.x == 0 and p.y == 1:
            return True
        else:
            l = (p.y ** 2) % self.q
            r = ((p.x ** 3) + self.a * p.x + self.b) % self.q
            return l == r

    def double(self, P):
        '''
        Doubling a point P. (2P, P+P)
        2 * (0,1) = (0,1)
        '''
        # print P, self.is_valid(P)
        if P.x is 0 and P.y is 1:
            # print P
            return Coord(0, 1)
        pente = ((3 * pow(P.x, 2) + self.a)
                 * tools.inversemodp(2 * P.y, self.q)) % self.q
        if (pente is 0 and P.y is 0 and P.x is not 0):
            # print "Catch error!",P
            return Coord(0, 1)
        else:
            x = (pow(pente, 2, self.q) - 2 * P.x) % self.q
            y = (pente * (P.x - x) - P.y) % self.q
            # print Coord(x,y),"doubling ",P
            return Coord(x, y)

    def double_and_add(self, P, n):
        '''
        Function to calculate n*P
        Uses double and add algorithm with binary represenation
        of number n
        '''
        binary = list(bin(n)[2:])
        r = Coord(0, 0)
        for item in binary:
            r = self.double(r)
            if (item == "1"):
                r = self.add(r, P)
        return r

    def inverse(self, P):
        return Coord(P.x, -P.y % self.q)


class Montgomery(Curve):

    def __init__(self, a, b, q,order):
        """
        elliptic curve in the Montgomert form:
        (b*y**2 = x**3 +A x**2 +x mod q
        - a,b: parameters of curve formula
        - q: prime number
        """
        self.a = a
        self.b = b
        self.q = q
        self.order = order

    def at(self, x, sbit):
        """
        find coordinate of a point at x
                x is X coordinate of point
                sbit is the sign bit
        """
        assert x < self.q
        ysq = (((x ** 3) + (self.a * x**2) + x)
        * tools.inversemodp(self.b, self.q)) % self.q
        root = tools.mod_sqrt(ysq, self.q)
        # print root
        if root == 0:
            #print "no point at this x coordinate"
            return -1
        return Coord(x, root) if sbit is True else Coord(x, -root % self.q)

    def add(self, P, Q):
        '''
        https://en.wikipedia.org/wiki/Montgomery_curve#Addition
        x3 = b*(y2-y1)^2/(x2-x1)^2  -a-x1-x2
        y3 = (2*x1+x2+a)*(y2-y1)/(x2-x1) -b*(y2-y1)3/(x2-x1)3 -y1
        '''
        if P == Q:
            return self.double(P)
        elif P == Coord(-1, -1):
            return Q
        elif Q == Coord(-1, -1):
            return P
        elif Q.x == P.x:
            return Coord(-1, -1)
        else:
            _ = ((Q.x - P.x)**2) % self.q
            __ = ((self.b * (Q.y - P.y) ** 2) * tools.inversemodp(_, self.q)) % self.q
            x = (__ - self.a - P.x - Q.x) % self.q
            xx = Q.x - P.x
            yy = Q.y - P.y
            __ = (((2 * P.x + Q.x+self.a) * yy) * tools.inversemodp(xx, self.q)) % self.q
            __ = (__ - (self.b * yy**3) * tools.inversemodp(xx**3, self.q)) % self.q
            y = (__ - P.y) % self.q
            return Coord(x, y)

    def is_valid(self, p):
        '''
        Returns True if point on Curve
        Returns False otherwise
        '''
        if p.x == 0 and p.y == 1:
            return True
        else:
            l = (p.y ** 2) % self.q
            r = ((p.x ** 3) + self.a * p.x**2 + p.x) % self.q
            return l == r

    def double(self, P):
        '''
        https://en.wikipedia.org/wiki/Montgomery_curve#Doubling
        '''
        if P == Coord(-1, -1):
            return P
        elif P.y == 0:
            return Coord(-1, -1)
        __ = (4*P.x*(P.x**2 + self.a * P.x + 1)) % self.q
        inv = tools.inversemodp(__, self.q)
        x = (((P.x**2 - 1)**2) * inv) % self.q
        __ = (2 * self.b * P.y) % self.q
        inv = tools.inversemodp(__, self.q)
        __2 = ((2 * P.x + P.x + self.a) * (3 * P.x**2 + 2 * self.a * P.x + 1) * (inv)) % self.q
        __3 = ((self.b * (3 * P.x**2 + 2 * self.a * P.x + 1)**3)*tools.inversemodp(__**3, self.q)) % self.q
        y = (__2 - __3 - P.y) % self.q
        return Coord(x, y)

    def double_and_add(self, P, n):
        '''
        Function to calculate n*P
        Uses double and add algorithm with binary represenation
        of number n
        '''
        binary = list(bin(n)[2:])
        r = Coord(-1, -1)
        for item in binary:
            # print "will double",r,self.is_valid(r)
            r = self.double(r)
            # print "result",r
            if (item == "1"):
                # print "will add",r,P
                r = self.add(r, P)
                # print "result",r
        return r

    def inverse(self, P):
        if P == Coord(-1, -1):
            return P
        else:
            return Coord(P.x, - P.y % self.q)


class Edwards(object):

    def __init__(self, d, a, q,order):
        '''
        Edwards curve: ax^2 + y^2 = 1 + dx^2y^2
        q: prime number
        d: preferably non square so we don't have exceptional points!
        a: when a!=1 then is twisted edwards curve
        '''
        self.d = d
        self.q = q
        self.a = a
        self.order = order

    def at(self, x, sbit):
        """
        Given the x-coordinate, return the y coordinate of the corresponding point
        on the curve.
        y^2 = (1 - x^2) / (a - dx^2 )
        """
        xx = (x * x) % self.q
        num = (1 - xx) % self.q
        denom = (self.a - (self.d * xx)) % self.q
        yy = (num * tools.inversemodp(denom, self.q)) % self.q
        # print "y2 = ",yy
        root = tools.mod_sqrt(yy, self.q)
        if root == 0:
            #print "no point at this x coordinate"
            return -1
        return Coord(x, root) if sbit is True else Coord(x, -root % self.q)

    def add(self, P, Q):
        """
        Computes P + Q = R using Edwards elliptic curve addition.
        Complete when a is a square and d is a nonsquare
        x = (x1y2+x2y1)/(1 + dx1x2y1y2)
        y = (y1y2-ax1x2)/(1 - dx1x2y1y2)
        """
        # print "adding",P,Q
        x1, y1 = P.x, P.y
        x2, y2 = Q.x, Q.y
        __ = (self.d * x1 * x2 * y1 * y2) % self.q
        nominatorX = ((x1 * y2) + (y1 * x2)) % self.q
        nominatorY = ((y1 * y2) - (self.a * x1 * x2)) % self.q
        denomX = (1 + __) % self.q
        denomY = (1 - __) % self.q
        x = (nominatorX * tools.inversemodp(denomX, self.q)) % self.q
        y = (nominatorY * tools.inversemodp(denomY, self.q)) % self.q
        return Coord(x, y)

    def is_valid(self, p):
        '''
        Verifies the validity of a point on curve
        '''
        x, y = p.x, p.y
        xx = (x * x) % self.q
        yy = (y * y) % self.q
        left = ((self.a * xx) + yy) % self.q
        right = ((self.d * xx * yy) + 1) % self.q
        return left == right

    def double(self, P):
        '''
        Doubles a point P. On Edwards curve this is P+P
        '''
        return self.add(P, P)

    def double_and_add(self, P, n):
        '''
        Function to calculate n*P
        Uses double and add algorithm with binary represenation
        of number n

        Side channel attack resistant as double and add
        operations are exactly the same!
        '''
        binary = list(bin(n)[2:])
        r = Coord(0, 1)
        for item in binary:
            # print "will double",r,self.is_valid(r)
            r = self.double(r)
            # print "result",r
            if (item == "1"):
                # print "will add",r,P
                r = self.add(r, P)
                # print "result",r
        return r

    def inverse(self, P):
        '''
        Gives the inverse point of the point P
        For Edwards curve this is (-x,y)
        '''
        # assert self.is_valid(P) is True, "Inverse of a point not on the curve"
        return Coord(- P.x % self.q, P.y)
