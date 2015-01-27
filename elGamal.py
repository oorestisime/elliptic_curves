import random
import collections
import tools as tools
import curve as ecc
import timeit as time
import texts as texts
import math as math
import hashlib
Coord = collections.namedtuple("Coord", ["x", "y"])


class ElGamal(object):

    '''
    This is an implementation of El gamal encryption algorithm using
    Elliptic Curves
    '''

    def __init__(self, c):
        self.curve = c
        self.Pk = None
        self.Sk = None
        self.basePoint = self.generate_base_point()
        self.gen_key_pair()

    def generate_base_point(self):
        '''
        Generating a Base Point valid on the Curve
        '''
        x, y = 0, 0
        print " Generating basepoint... \n "
        while self.curve.is_valid(Coord(x, y)) is False or (x == 0 and y == 0):
            x = random.randint(1, self.curve.q - 1)
            point = self.curve.at(x, True)
            if point is not -1:
                tmp = random.randint(1, self.curve.q - 1)
                x, y = self.curve.double_and_add(point, tmp)
            else:
                x = 0
                y = 0

        return Coord(x, y)

    def gen_key_pair(self):
        '''
        Generating a KeySet (Public and Private Key)
        '''
        self.Sk = PrivateKey(self.curve.order)
        self.Pk = PublicKey(self.curve, self.Sk, self.basePoint)

    def encrypt(self, P):
        '''
        Encrypt a point P
        '''
        assert self.curve.is_valid(
            P) is True, "Trying to encrypt point not on curve"
        r = random.randint(1, self.curve.order)
        R = self.curve.double_and_add(self.basePoint, r)
        __ = self.curve.double_and_add(self.Pk.point, r)
        cipher = self.curve.add(P, __)
        return texts.CipherText([R, cipher, __]), r

    def decrypt(self, Cipher):
        '''
        Decrypt a cipher text
        '''
        R, c, __ = Cipher.getCipher()
        S = self.curve.double_and_add(R, self.Sk.k)
        invPoint = self.curve.inverse(S)
        plaintext = self.curve.add(invPoint, c)
        return plaintext

    def reencrypt(self, Cipher):
        '''
        Reencrypt cipher with fresh randomness

        R: r*B
        C: P + Pub*r = P + B*r*s

        To re-encrypt:

        R: r*B+r2*B = B(r+r2)
        C: P + B*r*s + B*r2*s = P + B*s*(r+r2)
        '''
        R, c, pok = Cipher.getCipher()
        r = random.randint(1, self.curve.order)
        R2 = self.curve.add(R, self.curve.double_and_add(self.basePoint, r))
        __ = self.curve.double_and_add(self.Pk.point, r)
        cipher2 = self.curve.add(__, c)
        return texts.CipherText([R2, cipher2, __]), r

    def chaum_pedersen_ddh(self, g, y, w, u, r):
        '''
        Proover sends (a,b)=(s*g,s*y) s random
        Verifier sends random c
        Proover sends t=(s+cr)
        Verifier check: g*t == a+w*c and y*t == b+u*c

        easily converted in disjunctive proove using fiat-shamir heuristic
        '''
        s = random.randint(1, self.curve.order)
        a = self.curve.double_and_add(g, s)
        b = self.curve.double_and_add(y, s)
        hash_object = hashlib.sha512(str(a.x))
        hex_dig = hash_object.hexdigest()
        c = long(hex_dig, 16) % self.curve.order
        t = (s + c * r) % self.curve.order
        left_hand = self.curve.double_and_add(g, t)
        right_hand = self.curve.add(a, self.curve.double_and_add(w, c))
        left_hand2 = self.curve.double_and_add(y, t)
        right_hand2 = self.curve.add(b, self.curve.double_and_add(u, c))
        if((left_hand == right_hand) and (left_hand2 == right_hand2)):
            print "DDH verified"
            return True
        else:
            print left_hand == right_hand
            print left_hand2 == right_hand2
            return False

    def reencrypt_proof(self, c1, c2, randomness):
        '''
        Prooves that re-encryption is correct.
        y = x*B
        B = basepoint
        (alpha_1,beta_1) = (r * B, m + y * r) 
        (alpha_2,beta_2) = (alpha_1+B*u,beta_1+B*u)
        SO
        alpha_2 - alpha_1 = beta_2 - beta_1 = u*B.
        '''
        B = self.basePoint
        y = self.Pk.point
        _ = self.curve.inverse(c1.a)
        first = self.curve.add(c2.a, _)
        __ = self.curve.inverse(c1.b)
        second = self.curve.add(c2.b, __)
        return self.chaum_pedersen_ddh(B, y, first, second, randomness)

    def baby_step_giant_step(self, Q, l):
        '''
        Baby step giant step. find x such as Q=xP
        '''
        P = self.basePoint
        root = long(math.ceil(math.sqrt(l)))
        print "gen ", P
        i = 0
        verify = list()
        while i < root:
            __ = self.curve.inverse(self.curve.double_and_add(P, i * root))
            verify.append(self.curve.add(Q, __))
            i += 1
        print "first while!"
        found = False
        i = 1
        while not found and i < root:
            print i, root
            key = self.curve.double_and_add(P, i)
            print key
            if (key in verify):
                print key, i
                return (i + root * verify.index(key)) % self.q
            i += 1
        return "Not found"

    def pollard(self, Q,P):
        P = P
        order = self.curve.order
        q = self.curve.q
        points = list()
        a_b = list()
        a_b.append([1, 0])
        points.append(P)
        _a, _b = tools.which_group(P, a_b[0], q)
        a_b.append([_a, _b])
        points.append(self.curve.add(
            self.curve.double_and_add(P, _a), self.curve.double_and_add(Q, _b)))
        found = points[0] == points[1]
        i = 1
        while not found:
            i += 1
            if len(points) < 2 * i:
                # generate missing points
                points, a_b = self.fill_points(points, a_b, 2 * i+1, P, Q, q)
            #print points
            print i,2*i,points[i],points[2 * i]
            found = points[i].x == points[2 * i].x and points[i].y == points[2 * i].y
        for z,item in enumerate(points):
        	print z,item
        print points[i], a_b[i], points[2 * i],a_b[2 * i]

        if i == 1:
            a, b = a_b[0]
        else:
            a, b = a_b[i]
            _a, _b = a_b[2 * i]
            print a,b,_a,_b 
        return ((_a - a) * tools.inversemodp((b - _b), order)) % order

    def fill_points(self,points, a_b, i, P, Q, q):
	    '''
	    Completing points up to i.
	    Used in pollards rho algorithm
	    '''
	    z = len(points)
	    while z < i:
	        _a,_b = tools.which_group(points[z-1],a_b[z-1],q)
	        a_b.insert((z),[_a, _b])
	        points.insert((z),self.curve.add(
	            self.curve.double_and_add(P, _a), self.curve.double_and_add(Q, _b)))
	        z+=1
	    return points,a_b


class PrivateKey (object):

    '''
    This class is a represenation of the Private Key for the cryptosystem.
    It contains a random number
    '''

    def __init__(self, q):
        self.k = random.randint(1, q - 1)

    def __str__(self):
        return "Private Key: {:d}".format(self.k)


class PublicKey (object):

    '''
    This class is a represenation of the Public Key for the cryptosystem.
    It contains a point which comes from k*Basepoint
    '''

    def __init__(self, c, s, b):
        self.point = c.double_and_add(b, s.k)

    def __str__(self):
        return "Public Key: {:d} , {:d} ".format(self.point.x, self.point.y)

if __name__ == "__main__":
    '''
    Edwards testing
    '''
    '''q =  2**521 - 1 
    a = 1716199415032652428745475199770348304317358825035826352348615864796385795849413675475876651663657849636693659065234142604319282948702542317993421293670108523
    curve = ecc.Edwards((-376014%q), 1, q,a)
    # print tools.jacobi(3617,(2**414 - 17))
    point = curve.at(102,True)
    print point
    #print curve.double_and_add(point,a)
    
    Alice = ElGamal(curve)
    #start_time = time.default_timer()
    # print "Alice: ", Alice.Pk
    print "\n===== ENCRYPTION ======\n"
    cipher,randomness = Alice.encrypt(point)
    print "\n===== RE_ECRYPTION ======\n"
    re_cipher,fresh_randomness = Alice.reencrypt(cipher)
    print "\n===== VERIFY Reencrypt ======\n"
    print Alice.reencrypt_proof(cipher,re_cipher,fresh_randomness)
    print "\n===== DECRYPTION ======\n"
    plain = Alice.decrypt(re_cipher)
    print "plain text was", point, " i got ", plain, point==plain
    #elapsed = time.default_timer() - start_time
    #print"---",elapsed," seconds ---"
    '''
    '''
    Montgomery
    '''
    #q = 2 ** 221 - 3
    #l = 3369993333393829974333376885877457343415160655843170439554680423128
    q = 47 
    l = 41
    curve = ecc.Weierstrass(34, 10, q, l)
    Alice = ElGamal(curve)
    point = Coord(30,26)
    print point
    P = point
    Q = curve.double_and_add(P,40)
    #print P
    print Alice.pollard(Q,P)
    '''points = list()
    a_b = list()
    a_b.append([1, 0])
    P = Coord(30,26)
    Q = curve.double_and_add(P,14)
    points.append(P)
    _a, _b = tools.which_group(P, a_b[0], q)
    a_b.append([_a, _b])
    points.append(curve.add(
        curve.double_and_add(P, _a), curve.double_and_add(Q, _b)))
    points, a_b = Alice.fill_points(points,a_b,10,P,Q,q) 
    for i,item in enumerate(points):
    	print i," ->> ",item, a_b[i]'''
    # print point
    #check = curve.double_and_add(point,10**6)
    # print tools.mod_sqrt(l-1,q)
    # print Alice.baby_step_giant_step(check,q)
    # print curve.double_and_add(point,l)
    # print tools.mod_sqrt(l,q)
    '''Alice = ElGamal(curve)
    print "Alice: ", Alice.Pk
    print "\n\n\n===== ENCRYPTION ======\n\n\n"
    cipher = Alice.encrypt(point)[0]
    print cipher
    print "\n===== RE_ECRYPTION ======\n"
    re_cipher,fresh_randomness = Alice.reencrypt(cipher)
    print "\n===== VERIFY Reencrypt ======\n"
    print Alice.reencrypt_proof(cipher,re_cipher,fresh_randomness)
    print "\n===== DECRYPTION ======\n"
    plain = Alice.decrypt(re_cipher)
    print "plain text was", point, " i got ", plain, point==plain'''
