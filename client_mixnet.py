#!/usr/bin/python
from websocket import create_connection
import json
import collections
import elGamal as ecdlp
import curve as ecc
import zkp as zkp
import texts as texts
import time

Coord = collections.namedtuple("Coord", ["x", "y"])

def get_list():
    '''
    Getting first a public key and then a list of votes
    '''
    __ = ws.recv()
    print __
    Pk = json.loads(__, object_hook = pk_decoder)
    __ = ws.recv()
    print __
    votes = json.loads(__, object_hook = cipher_decoder)
    print votes
    return Pk, votes


def anonymize():
    '''
    Getting a list, then mixing in public 
    and returning the result
    '''
    start_time = time.time()
    ws.send("Waiting")
    Pk, votes = get_list()
    print("--- %s seconds ---" % str(time.time() - start_time))
    start_time = time.time()
    mixed = zkp.public_mixing(curve, votes, Pk)
    print("--- %s seconds ---" % str(time.time() - start_time))
    #ws.send("Mixing")
    ws.send(json.dumps([cipher.__dict__ for cipher in mixed]))

def cipher_decoder(obj):
    a = Coord(obj['a'][0],obj['a'][1])
    b = Coord(obj['b'][0],obj['b'][1])
    return texts.CipherText([a,b])

def pk_decoder(obj):
    p = Coord(obj['point'][0],obj['point'][1])
    b = Coord(obj['basePoint'][0],obj['basePoint'][1])
    return ecdlp.PublicKey(b,p)


if __name__ == "__main__":     
    q = 2 ** 221 - 3
    l = 3369993333393829974333376885877457343415160655843170439554680423128
    curve = ecc.Montgomery(117050, 1, q, l)
    ws = create_connection("ws://localhost:8000/ws")

    while True:
        _ = ws.recv()
        print _
        if _ == None: 
            break
        elif _ == "Mix":
            anonymize()
