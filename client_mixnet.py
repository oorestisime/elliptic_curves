#!/usr/bin/python
from websocket import create_connection
import json
import elGamal as ecdlp
import curve as ecc
import cPickle as pickle

ws = create_connection("ws://localhost:8000/ws")
print "Sending 'Hello, World'..."
ws.send("Hello, World")
print "Sent"
print "Reeiving..."
result =  ws.recv()
print "Received '%s'" % result
result =  ws.recv()
Alice = pickle.loads(result)
print "Received",Alice
print Alice.Pk 

ws.close()