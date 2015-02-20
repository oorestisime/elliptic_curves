'''
Downloadable script to encrypt and proove a vote
'''
import sys
import os
import random
import collections
import curve as curve
import zkp as zkp
import pickle as pickle
import texts as texts
Coord = collections.namedtuple("Coord", ["x", "y"])

class PublicKey (object):
    def __init__(self, b,p):
        self.basePoint = b
        self.point = p

    def __str__(self):
        return "Public Key: {:d} , {:d} ".format(self.point.x, self.point.y)

def encrypt(curve, Pk, P):
    '''
    Encrypt a point P
    '''
    assert curve.is_valid(P) is True or P is not Coord(-1,-1), "Trying to encrypt point not on curve"
    r = random.randint(1, curve.order)
    R = curve.double_and_add(Pk.basePoint, r)
    __ = curve.double_and_add(Pk.point, r)
    cipher = curve.add(P, __)
    return texts.CipherText([R, cipher]), r

def write_result(cipher):
    output = open("./encryption.txt", 'w+')
    pickle.dump(cipher,output)
    output.close() 


if __name__ == "__main__":
    if os.path.isfile("curve.txt"): 
        infile = open("curve.txt", 'r')
        curve = pickle.load(infile)
    else:
        print "Error reading curve"
        sys.exit()
    if os.path.isfile("pk.txt"): 
        infile = open("pk.txt", 'r')
        pk = pickle.load(infile)
    else:
        print "Error reading Public Key"
        sys.exit()
    if sys.argv[1] == 0:
        cipher, r = encrypt(curve,pk,Coord(-1,-1))
        __ = cipher.b
    else:
        cipher, r = encrypt(curve,pk,pk.basePoint)
        __ = curve.add(cipher.b,curve.inverse(pk.basePoint))
    if zkp.disjunction_proof(curve,__,pk,r) is True:
        print "Encryption prooved"
        write_result(cipher)
    else:
        print "Proof failed start again"



