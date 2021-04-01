from flask import Flask, render_template, Response, jsonify, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oghbs.db'
db = SQLAlchemy(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

curUserId = -1
checkInDate = datetime.now()
checkOutDate = datetime.now()
srt = '0'
foodId = '0'
availableOnly = '0'

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


class GuestHouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(60))
    description = db.Column(db.String(60))


class Rooms(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    floor = db.Column(db.Integer)
    type = db.Column(db.String(40))
    description = db.Column(db.String(60))  # Room type, no of beds
    status = db.Column(db.String(100))
    ghId = db.Column(db.Integer)
    pricePerDay = db.Column(db.Integer)
    occupancy = db.Column(db.Integer)
    ac = db.Column(db.Integer)


class FoodOptions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pricePerDay = db.Column(db.Integer)
    type = db.Column(db.String(40))


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
        print(request.form['password'])
        if user is not None and user.password == request.form['password']:
            global curUserId
            curUserId = user.id
            return render_template('calender.html', user=user)
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

def checkAvailable(room):
    global checkInDate
    global checkOutDate
    temp = checkInDate - datetime.now()
    checkInIndex = temp.days
    temp = checkOutDate - datetime.now()
    checkOutIndex = temp.days
    if checkInIndex < 0 or checkOutIndex < 0:
        return False
    for i in room.status[checkInIndex:checkOutIndex+1]:
        if i == '1':
            return False
    return True


rooms = []
avail = []
days = []
urls = []

@app.route('/viewrooms', methods=["POST", "GET"])
def ViewRooms():
    global checkInDate
    global checkOutDate
    global srt
    global foodId
    global availableOnly
    global rooms
    global avail
    global days
    global urls

    if 'availableOnly' in request.form:
        print("checking availability")
        if request.form['availableOnly'] == '1':
            availableOnly = '1'
            rooms = [i for i in rooms if checkAvailable(i)]
        else:
            availableOnly = '0'
            rooms = Rooms.query.all()

    elif 'srt' in request.form:
        print("sorting")
        if request.form['srt'] == '0':
            srt = '0'
            rooms.sort(key=lambda x: x.pricePerDay)
        else:
            srt = '1'
            rooms.sort(key=lambda x: x.pricePerDay, reverse=True)
    if 'foodId' in request.form:
        print("addind food")

        for i in rooms:
            temp = Rooms.query.filter_by(id=i.id).first()
            i.pricePerDay = temp.pricePerDay
        foodId = request.form['foodId']

        idx = int(foodId)
        foodItem = FoodOptions.query.filter_by(id=idx).first()
        if foodItem is not None:
            for i in rooms:
                i.pricePerDay += foodItem.pricePerDay
    else:
        print("called")
        if 'checkintime' in request.form:
            checkindate = datetime.strptime(request.form['checkintime'], '%Y-%m-%d')
            checkoutdate = datetime.strptime(request.form['checkouttime'], '%Y-%m-%d')
            checkInDate = checkindate
            checkOutDate = checkoutdate
        print("called")
        print(checkInDate)
        print(checkOutDate)
        if availableOnly == '1':
            rooms = [i for i in rooms if checkAvailable(i)]
        else:
            rooms = Rooms.query.all()
        if srt == '0':
            rooms.sort(key=lambda x: x.pricePerDay)
        else:
            rooms.sort(key=lambda x: x.pricePerDay, reverse=True)
        if foodId != '0':
            for i in rooms:
                temp = Rooms.query.filter_by(id=i.id).first()
                i.pricePerDay = temp.pricePerDay
            idx = int(foodId)
            foodItem = FoodOptions.query.filter_by(id=idx).first()
            if foodItem is not None:
                for i in rooms:
                    i.pricePerDay += foodItem.pricePerDay
        curdate = datetime.now()
        startDay = max(curdate, checkInDate-timedelta(days=3)) - curdate
        startIdx = startDay.days
        startdate = max(curdate, checkInDate-timedelta(days=3))
        for i in range(7):
            temp = startdate + timedelta(days=i)
            days.append(temp.day)
        for room in rooms:
            temp = []
            urls.append("/room/"+str(room.id))
            for j in range(7):
                temp.append(int(room.status[startIdx+j]))
            avail.append(temp)

    print(len(rooms))
    return render_template('Booking.html', rooms=rooms, avail=avail, days=days, urls=urls, availableOnly=availableOnly, srt=srt, foodId=foodId)


@app.route('/room/<roomid>', methods=["POST", "GET"])
def room(roomid):
    print("room is")
    print(roomid)
    return render_template('Payment.html')


# @app.route('/main', methods=["POST", "GET"])


if __name__ == '__main__':
    app.run()
