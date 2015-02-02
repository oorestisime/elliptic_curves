from flask import Flask
from tornado.wsgi import WSGIContainer
import tornado.ioloop as ioloop
import tornado.web as web
import tornado.websocket as websocket
import tornado.template
import elGamal as ecdlp
import curve as ecc
import tools as tools
import texts as texts
import collections
import json
Coord = collections.namedtuple("Coord", ["x", "y"])


class MainHandler(web.RequestHandler):

    def get(self):
        loader = tornado.template.Loader(".")
        self.write("hello from tornado")



class WSHandler(websocket.WebSocketHandler):

    def open(self):
        print 'connection opened...'
        #self.write_message(
            #"The server says: 'Hello'. Connection was accepted.")

    def on_message(self, message):
        print 'received:', message
        if message == "Waiting":
            print "sending"
            self.write_message(json.dumps(Alice.Pk.__dict__))
            retrieved = tools.retrieve_list("test")
            self.write_message(json.dumps([cipher.__dict__ for cipher in retrieved]))
        else:
            votes = json.loads(message, object_hook = cipher_decoder)
            #print votes
            tally = Alice.tallying(votes)
            print "searching"
            #print Alice.find_solution(Alice.decrypt(tally))
            print "\nThe candidate 1 has, ",Alice.find_solution(Alice.decrypt(tally))," votes out of ",len(votes),"\n"
            #print votes

    def on_close(self):
        print 'connection closed...'

app = Flask(__name__)
tr = WSGIContainer(app)

application = web.Application([
    (r'/ws', WSHandler),
    (r'/', MainHandler),
    (r".*", web.FallbackHandler, dict(fallback=tr)),
])

def cipher_decoder(obj):
    a = Coord(obj['a'][0],obj['a'][1])
    b = Coord(obj['b'][0],obj['b'][1])
    return texts.CipherText([a,b])


@app.route('/testing')
def hello_world():
    vote1 = Alice.basePoint
    vote2 = Coord(-1,-1)
    votes = list()
    
    print "\n===== ENCRYPTION of Votes ======\n"
    votes.append(Alice.encrypt(vote1)[0])
    print votes[0]
    votes.append(Alice.encrypt(vote1)[0])
    votes.append(Alice.encrypt(vote1)[0])
    print "\n Saving file \n"
    print votes
    tools.save_list(votes,"test")
    print "\n Retrieving\n"
    retrieved = tools.retrieve_list("test")
    print retrieved
    print "\n completing\n"
    retrieved.append(Alice.encrypt(vote2)[0])
    retrieved.append(Alice.encrypt(vote2)[0])
    print retrieved[0]
    tools.save_list(retrieved,"test")
    return 'This comes from Flask ^_^'


if __name__ == "__main__":
    application.listen(8000)
    q = 2 ** 221 - 3
    l = 3369993333393829974333376885877457343415160655843170439554680423128
    curve = ecc.Montgomery(117050, 1, q, l)
    Alice = ecdlp.ElGamal(curve)
    tornado.ioloop.IOLoop.instance().start()
