import random
import collections
import tools as tools
import curve as ecc
import timeit as time
import texts as texts
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
            y = self.curve.at(x, True)[1]
            tmp = random.randint(1, self.curve.q - 1)
            x, y = self.curve.double_and_add(Coord(x, y), tmp)

        return Coord(x, y)

    def gen_key_pair(self):
        '''
        Generating a KeySet (Public and Private Key)
        '''
        self.Sk = PrivateKey(self.curve.q)
        self.Pk = PublicKey(self.curve, self.Sk, self.basePoint)

    def encrypt(self, P):
        '''
        Encrypt a point P
        '''
        assert self.curve.is_valid(P) is True, "Trying to encrypt point not on curve"
        r = random.randint(1, self.curve.q - 1)
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
        r = random.randint(1, self.curve.q - 1)
        R2 = self.curve.add(R, self.curve.double_and_add(self.basePoint, r))
        __ = self.curve.double_and_add(self.Pk.point, r)
        cipher2 = self.curve.add(__, c)
        return texts.CipherText([R2, cipher2, __]),r

    def chaum_pedersen_ddh(self, g, y, w, u, r):
        '''
        Proover sends (a,b)=(s*g,s*y) s random
        Verifier sends random c
        Proover sends t=(s+cr)
        Verifier check: g*t == a+w*c and y*t == b+u*c

        easily converted in disjunctive proove using fiat-shamir heuristic
        '''
        s = random.randint(1, self.curve.q - 1)
        a = self.curve.double_and_add(g, s)
        b = self.curve.double_and_add(y, s)
        c = random.randint(1, self.curve.q - 1)
        t = (s + c * r)
        left_hand = self.curve.double_and_add(g, t)
        right_hand = self.curve.add(a, self.curve.double_and_add(w, c))
        left_hand2 = self.curve.double_and_add(y, t)
        right_hand2 = self.curve.add(b, self.curve.double_and_add(u, c))
        if((left_hand == right_hand) and (left_hand2 == right_hand2)):
            print "DDH verified"
            return True
        else:
            return False

    def reencrypt_ddh(self,c1,c2):
        '''
        Prooves that re-encryption is correct using DDH
        Proover needs to proove that the tuple 
        (g,y,(r*B - r2*B), (m1+Pk*r) - (m2+Pk*r2)) is a valid DDH tuple
        '''
        g = self.basePoint
        y = self.Pk
        _ = self.curve.inverse(c2.a)
        w = self.curve.add(c1.a, _)
        __ = self.curve.inverse(c2.b)
        u = self.curve.add(c1.a, __)
        return self.chaum_pedersen_ddh(g, y, w, u)

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
    q = 2**414 - 17
    '''
    Edwards testing
    '''
    curve = ecc.Edwards(3617, 1, q)
    # print tools.jacobi(3617,(2**414 - 17))
    point = curve.at(80, True)
    Alice = ElGamal(curve)
    start_time = time.default_timer()
    # print "Alice: ", Alice.Pk
    print "\n===== ENCRYPTION ======\n"
    cipher,randomness = Alice.encrypt(point)
    # print cipher
    print "\n===== VERIFY DDH ======\n"
    print Alice.chaum_pedersen_ddh(Alice.basePoint, Alice.Pk.point, cipher.a, cipher.pok, randomness)
    print "\n===== RE_ECRYPTION ======\n"
    re_cipher,fresh_randomness = Alice.reencrypt(cipher)
    # print cipher
    print "\n===== VERIFY Reencrypt ======\n"
    print Alice.reencrypt_ddh(cipher,re_cipher)
    print "\n===== DECRYPTION ======\n"
    plain = Alice.decrypt(re_cipher)
    print "plain text was", point, " i got ", plain, point==plain
    elapsed = time.default_timer() - start_time
    print"---",elapsed," seconds ---"

    '''
    Montgomery
    '''
    '''curve = ecc.Montgomery(7,1,q)
    point = curve.at(80,True)
    print point
    Alice = ElGamal(curve)
    print "Alice: ", Alice.Pk
    print "Secret: ",Alice.Sk
    print "\n\n\n===== ENCRYPTION ======\n\n\n"
    cipher = Alice.encrypt(point)
    print cipher
    print "\n===== RE_ECRYPTION ======\n"
    cipher = Alice.reencrypt(cipher)
    print cipher
    print "\n===== DECRYPTION ======\n"
    plain = Alice.decrypt(cipher)
    print "plain text was", point, " i got ", plain'''
