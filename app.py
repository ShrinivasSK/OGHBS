from flask import Flask, render_template, Response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oghbs.db'
db = SQLAlchemy(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


# user database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    address = db.Column(db.String(20))
    age = db.Column(db.Integer)
    relationToStd = db.Column(db.String(20), nullable=True)

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


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/regForm')
def reg_form():
    return render_template('regform.html')


if __name__ == '__main__':
    app.run()
