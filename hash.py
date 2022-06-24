import base64
from cgitb import reset
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import uuid
import bcrypt

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SECRET_KEY']='secret'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:Sychrldi227@localhost:5432/db_hash' 


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	public_id = db.Column(db.String, nullable=False)
	name = db.Column(db.String(30), nullable=False)
	username = db.Column(db.String(30), nullable=False, unique=True)
	email = db.Column(db.String(100), nullable=False, unique=True)
	password = db.Column(db.String(256), nullable=False)
	address = db.Column(db.Text)
	city = db.Column(db.String(255))
	state = db.Column(db.String(255))
	postcode = db.Column(db.Integer)
	phone = db.Column(db.BigInteger)
	is_admin = db.Column(db.Boolean, default=False)
	
	def __repr__(self):
		return f'<User "{self.name}">'

db.create_all()
db.session.commit()

@app.route('/auth/')
def author_user():
	decode_var = request.headers.get('Authorization')
	c = base64.b64decode(decode_var[6:])
	e = c.decode("ascii")
	lis = e.split(':')
	username = lis[0]
	passw = lis [1]
	user = User.query.filter_by(username=username).filter_by(password=passw).first()
	if bcrypt.checkpw(passw):
		print("match")
	else:
		print("does not match")	
	# if not user:
	# 	return 'Please check login detail'
	# elif user:
	# 	return [username, passw]

@app.route("/")
def home():
	return {
		"message" : "Welcome Vandina Coffee"
	}

@app.route('/register-hash/', methods=['POST'])
def register_user():
	data = request.get_json()
	passwords = data['password']
	bytePwd = passwords.encode('utf-8')
	salt = bcrypt.gensalt()
	hashed = bcrypt.hashpw(bytePwd, salt)
	if not 'name' in data or not 'username' in data or not 'password' in data:
		return jsonify({
			'error': 'Bad Request',
			'message': 'Name or username or password or email not given'
		}), 400
	if len(data['username']) < 4 or len(data['password']) < 6:
		return jsonify({
			'error': 'Bad Request',
			'message': 'Username must be contain minimum of 4 letters and Password must be contain minimum of 6 letters'
		}), 400
	user = User(
			name=data['name'], 
			username=data['username'],
			email=data['email'],
			password=hashed,
			address=data['address'],
			city=data['city'],
			state=data['state'],
			postcode=data['postcode'],
			phone=data['phone'],
			is_admin=data.get('is admin', False),
			public_id=str(uuid.uuid4())
		)
	db.session.add(user)
	db.session.commit()
	return {
		'id': user.public_id, 
		'name': user.name, 
		'username': user.username, 
		'email': user.email,
		'address': user.address,
		'city': user.city,
		'state': user.state,
		'postcode': user.email,
		'phone': user.phone,
		'is_admin': user.is_admin
	}, 201

@app.route('/login/')
def login_user():
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user.is_admin is True:
		return jsonify([
			{
				'id': user.public_id, 
				'name': user.name, 
				'username': user.username, 
				'email': user.email,
				'address': user.address,
				'city': user.city,
				'state': user.state,
				'postcode': user.email,
				'phone': user.phone,
				'is_admin': user.is_admin
			} for user in User.query.all()
		]), 200
	elif user.is_admin is False:
		return jsonify([
			{
				'id': user.public_id, 
				'name': user.name, 
				'username': user.username, 
				'email': user.email,
				'address': user.address,
				'city': user.city,
				'state': user.state,
				'postcode': user.email,
				'phone': user.phone,
				'is_admin': user.is_admin
			} 
		]), 200 
