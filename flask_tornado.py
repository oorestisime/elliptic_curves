from flask import Flask, render_template
from flask_flatpages import FlatPages
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

def cipher_decoder(obj):
    a = Coord(obj['a'][0],obj['a'][1])
    b = Coord(obj['b'][0],obj['b'][1])
    return texts.CipherText([a,b])


'''
Websocket server
'''
class WSHandler(websocket.WebSocketHandler):
    clients = []
    def open(self):
        WSHandler.clients.append(self)
        print 'connection opened...'
        #self.write_message("Mix")

    def on_message(self, message):
        print 'received:', message
        if message == "Waiting":
            print "sending"
            self.write_message(json.dumps(Alice.Pk.__dict__))
            retrieved = tools.retrieve_list("test")
            self.write_message(json.dumps([cipher.__dict__ for cipher in retrieved]))
        else:
            votes = json.loads(message, object_hook = cipher_decoder)
            tally = Alice.tallying(votes)
            print "searching"
            res = Alice.find_solution(Alice.decrypt(tally))
            print "\nThe candidate 1 has, ",res," votes out of ",len(votes),"\n"
            tools.write_result(res,votes,tools.retrieve_list("test"))
            #tornado.ioloop.IOLoop.instance().add_callback(result,res)

    def on_close(self):
        WSHandler.clients.remove(self)
        print 'connection closed...'

    @classmethod
    def ask_to_mix(cls):
        print "Writing to client"
        for client in cls.clients:
            client.write_message("Mix")

'''
Flask and Tornado config
'''
FLATPAGES_AUTO_RELOAD = True
FLATPAGES_EXTENSION = '.md'
app = Flask(__name__)
app.config.from_object(__name__)
pages = FlatPages(app)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
tr = WSGIContainer(app)

application = web.Application([
    (r'/ws', WSHandler),
    (r".*", web.FallbackHandler, dict(fallback=tr)),
])

'''
Routing URLS
'''

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


@app.route('/over')
def over():
    tornado.ioloop.IOLoop.instance().add_callback(WSHandler.ask_to_mix)
    return "Check completed elections to find results"

@app.route('/<path:path>/')
def page(path):
    #print pages.get(path)
    page = pages.get_or_404(path)
    print "res",page
    return render_template('page.html', page=page)



if __name__ == "__main__":
    application.listen(8000)
    q = 2 ** 221 - 3
    l = 3369993333393829974333376885877457343415160655843170439554680423128
    curve = ecc.Montgomery(117050, 1, q, l)
    Alice = ecdlp.ElGamal(curve)
    tornado.ioloop.IOLoop.instance().start()