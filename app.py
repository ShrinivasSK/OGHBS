from flask import Flask, render_template, Response, jsonify, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oghbs.db'
db = SQLAlchemy(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

curUserId = -1;

# user database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    address = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    rollStd = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return '<Name %r>' % self.id


# prevent cached responses
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


@app.route('/loginDetails', methods=['POST'])
def getDetails():
    json = request.get_json()
    print(json)

    return jsonify(result="done")


@app.route('/', methods=["POST", "GET"])
def hello_world():
    if request.method == "POST":
        print(request.form['username'])
        user = User.query.filter_by(username=request.form['username']).first()
        print(user.password)
        print(request.form['password'])
        if user is not None and user.password == request.form['password']:
            global curUserId
            curUserId = user.id
            return render_template('main.html', user=user)
        else:
            return render_template('index.html', flag=0)
    return render_template('index.html', flag=1)


@app.route('/regForm', methods=["POST", "GET"])
def reg_form():
    if request.method == "POST":
        nextId = User.query.count()+1
        print(nextId)
        name = request.form['first_name'] + request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        gender = request.form['gender']
        age = request.form['age']
        address = request.form['address1']+", "+request.form['address2']+", City "+request.form['city']+", State "+request.form['state']
        rollStd = request.form['roll']
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None:
            newUser = User(id=nextId, name=name, username=username, password=password, address=address, age=age, gender=gender, rollStd=rollStd)
        else:
            return render_template('regform.html', flag=0)
        # push to db
        try:
            db.session.add(newUser)
            db.session.commit()
            print("added successfully")
            return redirect('/')
        except:
            print("failed to add user to db")
    return render_template('regform.html', flag=1)

# @app.route('/main', methods=["POST", "GET"])


if __name__ == '__main__':
    app.run()
