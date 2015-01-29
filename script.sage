order = 0
p = 218993	
while not(is_prime(order)) or order == p or order == p+1:
    A = int(random()*100)
    B = int(random()*100)
    if (4*A^3 + 27*B^2).mod(p) != 0:
        E = EllipticCurve(GF(p),[A,B])
        order = E.cardinality()
print A,B,E.cardinality()
