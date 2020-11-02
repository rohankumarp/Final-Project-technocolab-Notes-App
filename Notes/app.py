from flask import Flask, render_template, redirect, url_for,session
from flask_pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import jsonify,request
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)

app.secret_key="secret"

app.config['MONGO_URI'] = "mongodb://localhost:27017/User"

mongo=PyMongo(app)

@app.route('/')
def index():
    if 'name' in session:
        notes = mongo.db.notes.find({'name': session['name']})
        return render_template('index.html',notes=notes)
    else:
        return render_template('login.html')

##############################################################################################

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        _name = request.form['name']
        _password = request.form['pwd']
        exist = mongo.db.user.find_one({'name':_name})
        if exist:
            if check_password_hash(exist['pwd'],_password):
                session['name']=_name

                return redirect(url_for('index'))
    return render_template('login.html')

##############################################################################################

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':

        _name=request.form['name']
        _email = request.form['email']
        _password = request.form['pwd']
        users=mongo.db.user
        exist=users.find_one({'name':_name})
        if exist is None:
            #h_p = bcrypt.hashpw(_password.encode('utf-8'),bcrypt.genSalt())
            _hashed = generate_password_hash(_password)
            mongo.db.user.insert({'name': _name, 'email': _email, 'pwd': _hashed})
            session['name']=_name
            #return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
        return redirect(url_for('index'))
    return render_template('register.html')

##########################################################################################

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': "not found"+request.url
    }
    res=jsonify(message)
    res.status_code=404
    return res
############################################################################################

@app.route('/users')
def users():
    users = mongo.db.user.find()
    res = dumps((users))
    return res
#####################################################################################################

@app.route('/add_notes',methods=['POST'])
def add_notes():
    _note = request.form['msg']
    if _note and request.method=='POST':
        mongo.db.notes.insert({'name':session['name'],'note':_note})
    return redirect(url_for('index'))

#######################################################################################################

@app.route('/logout',methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))
##########################################################################################################

@app.route('/remove')
def remove_note():
    key=request.args.get("_id")
    mongo.db.notes.remove({"_id":ObjectId(key)})
    return redirect(url_for('index'))


###################################################################################

if __name__ == '__main__':
    app.run(debug=True)