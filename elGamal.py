import random
import collections
import tools as tools
import curve as ecc
import timeit as time
import texts as texts
import math as math
import zkp as zkp
import hashlib
import time
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
        self.Pk = PublicKey(
            self.basePoint, self.curve.double_and_add(self.basePoint, self.Sk.k))

    def encrypt(self, P):
        '''
        Encrypt a point P
        '''
        assert self.curve.is_valid(
            P) is True or P is not Coord(-1, -1), "Trying to encrypt point not on curve"
        r = random.randint(1, self.curve.order)
        R = self.curve.double_and_add(self.basePoint, r)
        __ = self.curve.double_and_add(self.Pk.point, r)
        cipher = self.curve.add(P, __)
        return texts.CipherText([R, cipher]), r

    def decrypt(self, Cipher):
        '''
        Decrypt a cipher text
        '''
        R, c = Cipher.getCipher()
        S = self.curve.double_and_add(R, self.Sk.k)
        invPoint = self.curve.inverse(S)
        plaintext = self.curve.add(invPoint, c)
        return plaintext

    def tallying(self, votes):
        '''
        Homomorphic tallying

        '''
        _b = Coord(-1, -1)
        _a = Coord(-1, -1)
        for cipher in votes:
            _b = self.curve.add(_b, cipher.b)
            _a = self.curve.add(_a, cipher.a)
        return texts.CipherText([_a, _b])

    def find_solution(self, plain):
        '''
        Solving Q=xP finding x
        '''
        i = 0
        while self.curve.double_and_add(self.Pk.basePoint, i) != plain:
            i += 1
            # print i
        return i


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
    It contains a point which comes from k*Basepoint and the Basepoint
    '''

    def __init__(self, b, p):
        self.basePoint = b
        self.point = p

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
    q = 2 ** 221 - 3
    l = 3369993333393829974333376885877457343415160655843170439554680423128
    curve = ecc.Montgomery(117050, 1, q, l)
    Alice = ElGamal(curve)
    vote1 = Alice.basePoint
    '''cipher,r = Alice.encrypt(vote1)
    __ = curve.add(cipher.b,curve.inverse(vote1))
    print zkp.disjunction_proof(curve,__,Alice.Pk,r)'''
    vote2 = Coord(-1, -1)
    votes = list()
    c = Alice.encrypt(vote1)[0]
    start_time = time.time()
    print Alice.decrypt(c)
    print("--- %s seconds ---" % str(time.time() - start_time))

    for i in range(0, 100):
        if random.random() < 0.5:
            votes.append(Alice.encrypt(vote1)[0])
        else:
            votes.append(Alice.encrypt(vote2)[0])
    print("--- %s seconds ---" % str(time.time() - start_time))
    '''for i in range(0,10):
        if random.random() < 0.5:
            print "hre"
            print Alice.encrypt(vote1)[1]
            votes.append(Alice.encrypt(vote1)[1])
        else:
            print "there"
            cipher,_=Alice.encrypt(vote1)
            votes.append(cipher)
    print("--- %s seconds ---" % str(time.time() - start_time))
    print votes'''
    '''print "\n===== ENCRYPTION of Votes ======\n"
    votes.append(Alice.encrypt(vote1)[0])
    votes.append(Alice.encrypt(vote1)[0])
    votes.append(Alice.encrypt(vote1)[0])
    votes.append(Alice.encrypt(vote2)[0])
    votes.append(Alice.encrypt(vote2)[0])
    
    print votes
    print "\n===== Publix mixing ======\n"
    votes = zkp.public_mixing(curve,votes,Alice.Pk)
    print votes
    
    print "\n===== DECRYPTION ======\n"
    tally = Alice.tallying(votes)
    Alice.find_solution(Alice.decrypt(tally))'''

    '''
    Weierstrass testing
    '''
    '''q = 104395301 
    l = 104391409
    curve = ecc.Weierstrass(20, 25, q, l)
    point = curve.at(33,True)
    print point
    Alice = ElGamal(curve)
    print "\n===== ENCRYPTION ======\n"
    cipher,randomness = Alice.encrypt(point)
    print "\n===== RE_ECRYPTION ======\n"
    re_cipher,fresh_randomness = Alice.reencrypt(cipher)
    print "\n===== VERIFY Reencrypt ======\n"
    print Alice.reencrypt_proof(cipher,re_cipher,fresh_randomness)
    print "\n===== DECRYPTION ======\n"
    plain = Alice.decrypt(re_cipher)
    print "plain text was", point, " i got ", plain, point==plain'''
