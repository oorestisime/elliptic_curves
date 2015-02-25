import curve as ecc
import random
import texts as texts
import hashlib

def reencrypt(curve, Cipher, Pk):
        '''
        Reencrypt cipher with fresh randomness

        R: r*B
        C: P + Pub*r = P + B*r*s

        To re-encrypt:

        R: r*B+r2*B = B(r+r2)
        C: P + B*r*s + B*r2*s = P + B*s*(r+r2)
        '''
        R, c = Cipher.getCipher()
        r = random.randint(1, curve.order)
        R2 = curve.add(R, curve.double_and_add(Pk.basePoint, r))
        __ = curve.double_and_add(Pk.point, r)
        cipher2 = curve.add(__, c)
        return texts.CipherText([R2, cipher2]), r

def disjunction_proof(curve,cipher, Pk, randomness):
    '''
    Proof of disjunction. c1 or c2
    '''
    # Simulating proof for cipher2
    x_2 = random.randint(1, curve.order)
    h_2 = curve.double_and_add(Pk.basePoint,x_2)
    s_2 = random.randint(1, curve.order)
    c_2 = random.randint(1, curve.order)
    q = random.randint(1, curve.order)
    # Calculating commitments
    y_2 = curve.add(curve.double_and_add(Pk.basePoint,s_2),
        curve.inverse(curve.double_and_add(h_2,c_2)))
    y_1 = curve.double_and_add(Pk.point,q)
    # Challenge by honest verifier. (Fiat-Shamir)
    hash_object = hashlib.sha512(str(y_1.x))
    hex_dig = hash_object.hexdigest()
    c = long(hex_dig, 16) % curve.order
    # calculating c_1 and terminating proof for cipher
    c_1 = (c - c_2) % curve.order
    s_1 = (q + c_1 * randomness) % curve.order

    # verifying proofs

    print "c1+c2=c",c_1,c_2, c == (c_1+c_2) %curve.order
    left_proof_1 = curve.double_and_add(Pk.point,s_1)
    right_proof_1 = curve.add(y_1,curve.double_and_add(cipher,c_1))
    print "Proof logarithme 1",s_1,Pk.basePoint,right_proof_1
    if left_proof_1 == right_proof_1:
        print True
    else:
        print "False"
        return False
    left_proof_2 = curve.double_and_add(Pk.basePoint,s_2)
    right_proof_2 = curve.add(y_2,curve.double_and_add(h_2,c_2))
    print "Proof logarithme 2",s_2,Pk.basePoint,right_proof_2
    if left_proof_2 == right_proof_2:
        print "True"
        return True
    else:
        print "False"
        return False

def chaum_pedersen_ddh(curve, Pk, w, u, r):
    '''
    Proover sends (a,b)=(s*g,s*y) s random
    Verifier sends random c
    Proover sends t=(s+cr)
    Verifier check: g*t == a+w*c and y*t == b+u*c

    easily converted in disjunctive proove using fiat-shamir heuristic
    '''
    y = Pk.point
    g = Pk.basePoint
    s = random.randint(1, curve.order)
    a = curve.double_and_add(g, s)
    b = curve.double_and_add(y, s)
    hash_object = hashlib.sha512(str(a.x))
    hex_dig = hash_object.hexdigest()
    c = long(hex_dig, 16) % curve.order
    t = (s + c * r) % curve.order
    left_hand = curve.double_and_add(g, t)
    right_hand = curve.add(a, curve.double_and_add(w, c))
    left_hand2 = curve.double_and_add(y, t)
    right_hand2 = curve.add(b, curve.double_and_add(u, c))
    if((left_hand == right_hand) and (left_hand2 == right_hand2)):
        #print "DDH verified"
        return True
    else:
        print "Proof not verified"
        return False

def reencrypt_proof(curve, c1, c2, Pk, randomness):
    '''
    Prooves that re-encryption is correct.
    y = x*B
    B = basepoint
    (alpha_1,beta_1) = (r * B, m + y * r) 
    (alpha_2,beta_2) = (alpha_1+B*u,beta_1+B*u)
    SO
    alpha_2 - alpha_1 = beta_2 - beta_1 = u*B.
    '''
    _ = curve.inverse(c1.a)
    first = curve.add(c2.a, _)
    __ = curve.inverse(c1.b)
    second = curve.add(c2.b, __)
    return chaum_pedersen_ddh(curve, Pk, first, second, randomness)


def public_mixing(curve,votes,Pk):
    '''
    Public mixing shuffles a list and re-ecrypts the votes.
    It calculates the necessary prooves of re-encryption

    It returns a new list shuffled and reencrypted 
    '''
    mixed = list()
    for cipher in votes:
        re_cipher, randomness = reencrypt(curve,cipher,Pk)
        print "Re-encryption: ",reencrypt_proof(curve, cipher, re_cipher, Pk, randomness)
        mixed.append(re_cipher)
    return sorted(mixed, key=lambda k: random.random())
