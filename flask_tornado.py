from flask import Flask
from tornado.wsgi import WSGIContainer
import tornado.ioloop as ioloop
import tornado.web as web
import tornado.websocket as websocket
import tornado.template
import elGamal as ecdlp
import curve as ecc
import tools as tools
import cPickle as pickle
import collections
Coord = collections.namedtuple("Coord", ["x", "y"])


class MainHandler(web.RequestHandler):

    def get(self):
        loader = tornado.template.Loader(".")
        self.write("hello from tornado")


class WSHandler(websocket.WebSocketHandler):

    def open(self):
        print 'connection opened...'
        self.write_message(
            "The server says: 'Hello'. Connection was accepted.")

    def on_message(self, message):
        # self.write_message("The server says: " + message + " back at you")
        self.write_message(pickle.dumps(Alice))
        print 'received:', message

    def on_close(self):
        print 'connection closed...'

app = Flask(__name__)
tr = WSGIContainer(app)

application = web.Application([
    (r'/ws', WSHandler),
    (r'/', MainHandler),
    (r".*", web.FallbackHandler, dict(fallback=tr)),
])


@app.route('/testing')
def hello_world():
    Alice = ecdlp.ElGamal(curve)
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
    tornado.ioloop.IOLoop.instance().start()
