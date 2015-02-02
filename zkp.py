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
        print "DDH verified"
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

def baby_step_giant_step(curve, Q, l):
    '''
    Baby step giant step. find x such as Q=xP
    '''
    P = curve.basePoint
    root = long(math.ceil(math.sqrt(l)))
    print "gen ", P
    i = 0
    verify = list()
    while i < root:
        __ = curve.inverse(curve.double_and_add(P, i * root))
        verify.append(curve.add(Q, __))
        i += 1
    print "first while!"
    found = False
    i = 1
    while not found and i < root:
        print i, root
        key = curve.double_and_add(P, i)
        print key
        if (key in verify):
            print key, i
            return (i + root * verify.index(key)) % curve.q
        i += 1
    return "Not found"

def pollard(curve, Q,P):
    P = P
    order = curve.order
    q = curve.q
    points = list()
    a_b = list()
    a_b.append([1, 0])
    points.append(P)
    _a, _b = tools.which_group(P, a_b[0], q)
    a_b.append([_a, _b])
    points.append(curve.add(
        curve.double_and_add(P, _a), curve.double_and_add(Q, _b)))
    found = points[0] == points[1]
    i = 1
    while not found:
        i += 1
        if len(points) < 2 * i:
            # generate missing points
            points, a_b = curve.fill_points(points, a_b, 2 * i+1, P, Q, q)
        #print points
        #print i,2*i,points[i],points[2 * i]
        found = points[i].x == points[2 * i].x and points[i].y == points[2 * i].y
        if (a_b[i] == a_b[2*i]):
            found = False
    '''for z,item in enumerate(points):
        print z,item
    print points[i], a_b[i], points[2 * i],a_b[2 * i]
    '''
    if i == 1:
        a, b = a_b[0]
    else:
        a, b = a_b[i]
        _a, _b = a_b[2 * i]
        print a,b,_a,_b 
    return ((_a - a) * tools.inversemodp((b - _b), order)) % order

def fill_points(curve,points, a_b, i, P, Q, q):
    '''
    Completing points up to i.
    Used in pollards rho algorithm
    '''
    z = len(points)
    while z < i:
        _a,_b = tools.which_group(points[z-1],a_b[z-1],q)
        a_b.insert((z),[_a, _b])
        points.insert((z),curve.add(
            curve.double_and_add(P, _a), curve.double_and_add(Q, _b)))
        z+=1
    return points,a_b

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
