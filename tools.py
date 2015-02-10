import random
import pickle
import os
import collections
'''
Tools for prime numbers
'''
Coord = collections.namedtuple("Coord", ["x", "y"])

def rabinMiller(num):
    # Returns True if num is a prime number.
    s = num - 1
    t = 0
    while s % 2 == 0:
        # keep halving s while it is even (and use t
        # to count how many times we halve s)
        s = s // 2
        t += 1
    for trials in range(5):  # try to falsify num's primality 5 times
        a = random.randrange(2, num - 1)
        v = pow(a, s, num)
        if v != 1:  # this test does not apply if v is 1.
            i = 0
            while v != (num - 1):
                if i == t - 1:
                    return False
                else:
                    i = i + 1
                    v = (v ** 2) % num
    return True


def isPrime(num):
    # Return True if num is a prime number. This function does a quicker
    # prime number check before calling rabinMiller().
    if (num < 2):
        return False  # 0, 1, and negative numbers are not prime
    # About 1/3 of the time we can quickly determine if num is not prime
    # by dividing by the first few dozen prime numbers. This is quicker
    # than rabinMiller(), but unlike rabinMiller() is not guaranteed to
    # prove that a number is prime.
    lowPrimes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443,
                 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]

    if num in lowPrimes:
        return True
    # See if any of the low prime numbers can divide num
    for prime in lowPrimes:
        if (num % prime == 0):
            return False
    # If all else fails, call rabinMiller() to determine if num is a prime.
    return rabinMiller(num)


def generateLargePrime(keysize):
    # Return a random prime number of keysize bits in size.
    while True:
        num = random.randrange(2 ** (keysize - 1), 2 ** (keysize))
        if isPrime(num):
            return num
'''
modular inverse
'''


def extended_gcd(aa, bb):
    lastremainder, remainder = abs(aa), abs(bb)
    x, lastx, y, lasty = 0, 1, 1, 0
    while remainder:
        lastremainder, (quotient, remainder) = remainder, divmod(
            lastremainder, remainder)
        x, lastx = lastx - quotient * x, x
        y, lasty = lasty - quotient * y, y
    return lastremainder, lastx * (-1 if aa < 0 else 1), lasty * (-1 if bb < 0 else 1)


def inversemodp(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise ValueError
    return x % m

'''
Modular square root!
'''


def mod_sqrt(a, p):
    """ Find a quadratic residue (mod p) of 'a'. p
        must be an odd prime.

        Solve the congruence of the form:
            x^2 = a (mod p)
        And returns x. Note that p - x is also a root.

        0 is returned is no square root exists for
        these a and p.

        The Tonelli-Shanks algorithm is used (except
        for some simple cases in which the solution
        is known from an identity). This algorithm
        runs in polynomial time (unless the
        generalized Riemann hypothesis is false).
    """
    # Simple cases
    #
    if legendre_symbol(a, p) != 1:
        return 0
    elif a == 0:
        return 0
    elif p == 2:
        return p
    elif p % 4 == 3:
        return pow(a, (p + 1) / 4, p)

    # Partition p-1 to s * 2^e for an odd s (i.e.
    # reduce all the powers of 2 from p-1)
    #
    s = p - 1
    e = 0
    while s % 2 == 0:
        s /= 2
        e += 1

    # Find some 'n' with a legendre symbol n|p = -1.
    # Shouldn't take long.
    #
    n = 2
    while legendre_symbol(n, p) != -1:
        n += 1

    x = pow(a, (s + 1) / 2, p)
    b = pow(a, s, p)
    g = pow(n, s, p)
    r = e

    while True:
        t = b
        m = 0
        for m in xrange(r):
            if t == 1:
                break
            t = pow(t, 2, p)

        if m == 0:
            return x

        gs = pow(g, 2 ** (r - m - 1), p)
        g = (gs * gs) % p
        x = (x * gs) % p
        b = (b * g) % p
        r = m


def legendre_symbol(a, p):
    """ Compute the Legendre symbol a|p using
        Euler's criterion. p is a prime, a is
        relatively prime to p (if p divides
        a, then a|p = 0)

        Returns 1 if a has a square root modulo
        p, -1 otherwise.
    """
    ls = pow(a, (p - 1) / 2, p)
    return -1 if ls == p - 1 else ls


def which_group(R, a_b, q):
    '''
    A method for determining in which group is a point.
    Used for pollard rho algorithm. 

    Returns the new a and b used for calculating next point
    '''
    if R.y < q / 3:
        _a = a_b[0]
        _b = a_b[1] + 1
    elif R.y >= q / 3 and R.y < (2 * q / 3):
        _a = (2 * a_b[0]) % q
        _b = (2 * a_b[1]) % q
    else:
        _a = a_b[0] + 1
        _b = a_b[1]
    return _a, _b

def create_file(name):
    '''
    Creating folder and file inside elections. 
    Storing inside the ciphertexts
    '''
    directory = "./elections/"+name
    if not os.path.exists(directory):
        os.makedirs(directory)
    new_file = open("./elections/"+name+"/db.txt", 'w+')
    new_file.close

def save_list(ciphers,directory):
    '''
    Adding a ciphertext inside the db
    '''
    output = open("./elections/"+directory+"/db.txt", 'w+')
    pickle.dump(ciphers,output)
    output.close() 

def retrieve_list(directory):
    '''
    read a file and deserialize
    '''
    infile = open("./elections/"+directory+"/db.txt", 'r')
    return pickle.load(infile)

def write_result(res,mixed,orig):
    new_file = open("./pages/elections/result.md", 'w+')
    new_file.write("Result is : %s\n" % res)
    new_file.write("\n\n\nNEW\n")
    for item in mixed:
        new_file.write("%s\n" % item)
    new_file.write("\n\nOrignal\n")
    for item in orig:
        new_file.write("%s\n" % item)

def parse_vote(vote):
    '''
    Coord(x=702671685038303812736048637156317122042145521167006925162182361873L, 
        y=2355424066487173446930943433041273479073009200461441713736213318168L)
    '''
    __ = vote.split(",")
    x = __[0][8:].strip("L)")
    y = __[1][3:].strip("L)")
    #print "the x",x
    #print "the y",y
    return Coord(long(x),long(y)) 