from flask import Flask, render_template, redirect, request,flash
from flask_flatpages import FlatPages
from flask.ext.wtf import Form
from werkzeug import secure_filename
from wtforms import StringField
from wtforms.validators import DataRequired
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
import zipfile
import os
import pickle
Coord = collections.namedtuple("Coord", ["x", "y"])

def cipher_decoder(obj):
    a = Coord(obj['a'][0],obj['a'][1])
    b = Coord(obj['b'][0],obj['b'][1])
    return texts.CipherText([a,b])


class NewElection(Form):
    unique_name = StringField('unique name', validators=[DataRequired()])

'''
Websocket server
'''
class WSHandler(websocket.WebSocketHandler):
    clients = []
    election_name = "nothing"
    def open(self):
        WSHandler.clients.append(self)
        print 'connection opened...'
        #self.write_message("Mix")

    def on_message(self, message):
        print 'received:', message
        if message == "Waiting":
            print "sending"
            self.write_message(json.dumps(Alice.Pk.__dict__))
            retrieved = tools.retrieve_list(WSHandler.election_name)
            self.write_message(json.dumps([cipher.__dict__ for cipher in retrieved]))
        else:
            votes = json.loads(message, object_hook = cipher_decoder)
            tally = Alice.tallying(votes)
            print "searching"
            res = Alice.find_solution(Alice.decrypt(tally))
            print "\nThe candidate 1 has, ",res," votes out of ",len(votes),"\n"
            tools.write_result(res,votes,tools.retrieve_list(WSHandler.election_name))
            #tornado.ioloop.IOLoop.instance().add_callback(result,res)

    def on_close(self):
        WSHandler.clients.remove(self)
        print 'connection closed...'

    @classmethod
    def ask_to_mix(cls,election_name):
        print "Writing to client, mixing",election_name
        cls.election_name = election_name
        for client in cls.clients:
            client.write_message("Mix")

'''
Flask and Tornado config
'''
SECRET_KEY = 'development'
FLATPAGES_AUTO_RELOAD = True
FLATPAGES_EXTENSION = '.md'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt'])
app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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

@app.route("/")
def index():
    elecs = [x[0].replace("./elections/","",1) for x in os.walk("./elections")]
    return render_template('index.html',election_list=elecs[1:])

@app.route('/add_random')
def hello_world():
    vote1 = Alice.basePoint
    vote2 = Coord(-1,-1)
    votes = tools.retrieve_list("test")
    
    print "\n===== ENCRYPTION of Votes ======\n"
    votes.append(Alice.encrypt(vote1)[0])
    votes.append(Alice.encrypt(vote1)[0])
    votes.append(Alice.encrypt(vote1)[0])
    votes.append(Alice.encrypt(vote2)[0])
    votes.append(Alice.encrypt(vote2)[0])
    tools.save_list(votes,"test")
    return 'Added Random votes'

@app.route('/new_election', methods=['GET', 'POST'])
def new_election():
    form = NewElection()
    if form.validate_on_submit():
        if os.path.exists("elections/"+form.unique_name.data):
            flash("Election already exists.")
        else:
            os.makedirs("elections/"+form.unique_name.data)
            flash('Created election %s ' % (form.unique_name.data))
        return redirect('/new_election')
    return render_template('create.html',form=form)

@app.route('/vote/')
def voting():
    redirect("/")

@app.route('/vote/<election_name>/', methods=('GET', 'POST'))
def vote(election_name):
    if not os.path.exists("elections/"+election_name):
        print election_name
        flash("Election does not exist. You can create a new one")
        return redirect("/new_election")
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            infile = open(UPLOAD_FOLDER+"/"+filename, 'r')
            vote = pickle.load(infile)
            print vote
            print "retrieving list and encrypting vote"
            retrieved = tools.retrieve_list(election_name)
            retrieved.append(vote)
            #print "lets see",Alice.decrypt(retrieved[-1]) is Alice.basePoint
            print "saving into file"
            tools.save_list(retrieved,election_name)
            print "length now",len(tools.retrieve_list(election_name))
            flash("Your vote has been registered!")
            return render_template('vote.html',name=election_name)
    return render_template('vote.html',name=election_name)

@app.route('/over/<election_name>/')
def over(election_name):
    #print len(tools.retrieve_list("test"))
    tornado.ioloop.IOLoop.instance().add_callback(callback= lambda: WSHandler.ask_to_mix(election_name))
    return "Check completed elections to find results"

@app.route('/<path:path>/')
def page(path):
    #print pages.get(path)
    page = pages.get_or_404(path)
    #print "res",page
    return render_template('page.html', page=page)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def create_zip():
    zf = zipfile.ZipFile('static/soft.zip', mode='w')
    try:
        print 'adding files'
        zf.write('curve.txt')
        zf.write('pk.txt')
        zf.write('soft.py')
        zf.write('curve.py')
        zf.write('zkp.py')
        zf.write('tools.py')
        zf.write('texts.py')
        zf.write('elGamal.py')
    finally:
        print 'closing'
        zf.close()

def clear():
    os.remove("elections/test/db.txt")
    os.remove("uploads/encryption.txt")
    os.remove("static/soft.zip")


if __name__ == "__main__":
    #clear()
    application.listen(8000)
    q = 2 ** 221 - 3
    l = 3369993333393829974333376885877457343415160655843170439554680423128
    curve = ecc.Montgomery(117050, 1, q, l)
    Alice = ecdlp.ElGamal(curve)
    tools.write_file(curve,"curve")
    tools.write_file(Alice.Pk,"pk")
    create_zip()
    tornado.ioloop.IOLoop.instance().start()
