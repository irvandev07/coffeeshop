import base64
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import uuid


app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SECRET_KEY']='secret'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:Sychrldi227@localhost:5432/db_coffeeshop' 


order_detail = db.Table('order_detail',
	db.Column('id', db.Integer, primary_key=True),
	db.Column('public_id', db.String),
	db.Column('quantity', db.Integer),
	db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
	db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	public_id = db.Column(db.String, nullable=False)
	name = db.Column(db.String(30), nullable=False)
	username = db.Column(db.String(30), nullable=False, unique=True)
	email = db.Column(db.String(100), nullable=False, unique=True)
	password = db.Column(db.String(100), nullable=False)
	address = db.Column(db.Text)
	city = db.Column(db.String(255))
	state = db.Column(db.String(255))
	postcode = db.Column(db.Integer)
	phone = db.Column(db.BigInteger)
	is_admin = db.Column(db.Boolean, default=False)
	# users = db.relationship('Order', backref='users', lazy=True )
	
	def __repr__(self):
		return f'<User "{self.name}">'

class Categories(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	public_id = db.Column(db.String, nullable=False)
	name_categories = db.Column(db.String(100), nullable=False)
	# categories = db.relationship('Products', backref='categories', lazy=True )

	def __repr__(self):
		return f'<Categories "{self.name_categories}">'

class Products(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	public_id = db.Column(db.String, nullable=False)
	name_product = db.Column(db.String(100), nullable=False)
	price = db.Column(db.Integer, nullable=False)
	quantity = db.Column(db.Integer, nullable=False)
	categories_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
	description = db.Column(db.Text)
	image = db.Column(db.Text)
	# products = db.relationship('order_detail', backref='products', lazy=True)

	def repr(self):
		return f'Products <{self.name_product}>'

class Order(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	public_id = db.Column(db.String, nullable=False)
	date = db.Column(db.Date, nullable=False)
	payment_type = db.Column(db.String(100), nullable=False)
	status = db.Column(db.String(100), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	# orders = db.relationship('order_detail', backref='orders', lazy=True)

	def repr(self):
		return f'Order <{self.status}>'	


db.create_all()
db.session.commit()

# @app.route('/auth')
def author_user(auth):
	decode_var = request.headers.get('Authorization')
	c = base64.b64decode(auth[6:])
	e = c.decode("ascii")
	lis = e.split(':')
	username = lis[0]
	passw = lis [1]
	user = User.query.filter_by(username=username).filter_by(password=passw).first()

	if not user:
		return 'Please check login detail'
	elif user:
		return [username, passw]

@app.route("/")
def home():
	return {
		"message" : "Welcome Vandina Coffee"
	}

@app.route('/register/', methods=['POST'])
def create_user():
	data = request.get_json()
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
			password=data['password'],
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
		'is admin': user.is_admin
	}, 201


@app.route('/login/')
def get_users():
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user:
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
				'is admin': user.is_admin
			} for user in User.query.all()
		]), 200


@app.route('/users/', methods=['PUT'])
def update_user():
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	allowpass = author_user(decode_var)[1]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user:
		data = request.get_json()
		if 'name' not in data:
			return {
				'error': 'Bad Request',
				'message': 'Name field needs to be present'
			}, 400
		user = User.query.filter_by(username=allow).filter_by(password=allowpass).first_or_404()
		if not user:
			return {'message' : 'Please check login detail!'}
		user.name=data['name']
		user.username=data['username']
		user.password=data['password']
		if 'name' in data:
			user.name=data['name']
		if 'username' in data:
			user.username=data['username']
		if 'password' in data:
			user.password=data['password']
		db.session.commit()
		return jsonify({
			'id': user.public_id, 'name': user.name, 'username': user.username, 'password': user.password,
		}),200