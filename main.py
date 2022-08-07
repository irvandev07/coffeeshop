import base64
from functools import wraps
from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime, timedelta
import uuid
import jwt
from flask_cors import CORS, cross_origin

app = Flask(__name__)
db = SQLAlchemy(app)
CORS(app, supports_credentials=True)

app.config['SECRET_KEY']='secret'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:Sychrldi227@localhost:5432/db_coffeeshop' 


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
	# image = db.Column(db.String(255))
	is_admin = db.Column(db.Boolean, default=False)
	users = db.relationship('Order', backref='users', lazy=True)
	
	def __repr__(self):
		return f'<User "{self.name}">'

class Categories(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	public_id = db.Column(db.String, nullable=False)
	name_categories = db.Column(db.String(100), nullable=False)
	categories = db.relationship('Products', backref='categories', lazy=True)

	def __repr__(self):
		return f'<Categories "{self.name_categories}">'

class Products(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	categories_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
	public_id = db.Column(db.String, nullable=False)
	name_product = db.Column(db.String(100), nullable=False)
	price = db.Column(db.Integer, nullable=False)
	stock = db.Column(db.Integer, nullable=False)
	description = db.Column(db.Text)
	image = db.Column(db.Text)
	products = db.relationship('OrderDetail', backref='products', lazy=True)

	def repr(self):
		return f'Products <{self.name_product}>'

class Order(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	public_id = db.Column(db.String, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	user_name = db.Column(db.String, nullable=False)
	date = db.Column(db.Date, nullable=False)
	payment_type = db.Column(db.String(100), nullable=False)
	status = db.Column(db.String(100), nullable=False)
	total_price = db.Column(db.Integer, nullable=False)
	orders = db.relationship('OrderDetail', backref='orders', lazy=True, cascade="all, delete")

	def repr(self):
		return f'Order <{self.status}>'	

class OrderDetail(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	public_id = db.Column(db.String, nullable=False)
	order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
	product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
	product_name = db.Column(db.String, nullable=False)
	quantity = db.Column(db.Integer, nullable=False)
	subtotal = db.Column(db.Integer, nullable=False)

	def repr(self):
		return f'Order <{self.status}>'	

class Cart(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	public_id = db.Column(db.String, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	product_id = db.Column(db.Integer, nullable=False)
	product_name = db.Column(db.String, nullable=False)
	quantity = db.Column(db.Integer, nullable=False)
	price = db.Column(db.Integer, nullable=False)
	image = db.Column(db.String, nullable=False)

	def repr(self):
		return f'Cart <{self.id}>'	

# db.create_all()
# db.session.commit()


def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None
		if 'x-access-token' in request.headers:
				token = request.headers['x-access-token']
		if not token:
				return jsonify({'message' : 'Token is missing !!'}), 401
		try:
				data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
				current_user = User.query.filter_by(username=data['username']).first()
		except:
				return jsonify({
						'message' : 'Token is invalid !!'
				}), 401
		return  f(current_user, *args, **kwargs)
	return decorated
		

@app.route('/login/' , methods=['POST'])
@cross_origin(supports_credentials=True)
def author_user():
	decode_var = request.headers.get('Authorization')
	c = base64.b64decode(decode_var[6:])
	e = c.decode("ascii")
	lis = e.split(':')
	username = lis[0]
	passw = lis [1]
	user = User.query.filter_by(username=username).filter_by(password=passw).first()
	if not user:
		return make_response(
				'Please check login detail'
		),401
	elif user:
		token = jwt.encode({
			'id': user.public_id ,'username': user.username, 'is_admin' : user.is_admin,
			'exp' : datetime.utcnow() + timedelta(hours = 24)
		}, app.config['SECRET_KEY'])
		return make_response(jsonify({'token' : token}), 201)

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
		"message" : "Welcome Copysop"
	}

@app.route('/register/', methods=['POST'])
@cross_origin(supports_credentials=True)
def register_user():
	data = request.get_json()
	if not 'name' in data or not 'username' in data or not 'password' in data:
		return jsonify({
			'error': 'Bad Request',
			'message': 'Name or username or password or email not given'
		}), 400
	if len(data['username']) < 4 or len(data['password']) < 4:
		return jsonify({
			'error': 'Bad Request',
			'message': 'Username must be contain minimum of 4 letters and Password must be contain minimum of 4 letters'
		}), 400
	user = User(
			name=data['name'], 
			username=data['username'],
			password=data['password'],
			is_admin=data.get('is admin', False),
			public_id=str(uuid.uuid4())
		)
	db.session.add(user)
	db.session.commit()
	return {
		'id': user.public_id, 
		'name': user.name, 
		'username': user.username, 
		'is_admin': user.is_admin
	}, 201

@app.route('/users/')
@token_required
def get_user(current_user):
	if not current_user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif current_user.is_admin is True:
		return jsonify([
			{
				'id': user.public_id, 
				'name': user.name, 
				'username': user.username, 
				'email': user.email,
				'address': user.address,
				'city': user.city,
				'state': user.state,
				'postcode': user.postcode,
				'phone': user.phone,
				'is_admin': user.is_admin
			} for user in User.query.all()
		]), 200
	elif current_user.is_admin is False:
		return jsonify([
			{
				'id': current_user.public_id, 
				'name': current_user.name, 
				'username': current_user.username, 
				'email': current_user.email,
				'address': current_user.address,
				'city': current_user.city,
				'state': current_user.state,
				'postcode': current_user.postcode,
				'phone': current_user.phone,
				'is_admin': current_user.is_admin
			} 
		]), 200 

@app.route('/users/', methods=['PUT'])
def update_user():
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	allowpass = author_user(decode_var)[1]
	user = User.query.filter_by(username=allow).filter_by(password=allowpass).first_or_404()
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
		if not user:
			return {'message' : 'Please check login detail!'}
		if 'name' in data:
			user.name=data['name']
		if 'username' in data:
			user.username=data['username']
		if 'email' in data:
			user.email=data['email']
		if 'password' in data:
			user.password=data['password']
		if 'address' in data:
			user.address=data['address']
		if 'city' in data:
			user.city=data['city']
		if 'state' in data:
			user.state=data['state']
		if 'postcode' in data:
			user.postcode=data['postcode']
		if 'phone' in data:
			user.phone=data['phone']
		db.session.commit()
		return jsonify(
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
		}),201

@app.route('/users/<id>/', methods=['DELETE'] )
def delete_user(id):
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user:
		user = User.query.filter_by(public_id=id).first_or_404()
		db.session.delete(user)
		db.session.commit()
		return {
			'success': 'Data deleted successfully'
		},200

#---------------------------------- CATEGORIES

@app.route('/categories/')
@token_required
def get_category(current_user):
	if not current_user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif current_user:
		return jsonify([
			{
				'id': categories.public_id, 
				'name_categories': categories.name_categories
			} for categories in Categories.query.order_by(Categories.id.desc()).all()
		]),200

@app.route('/categories/<id>/')
def get_categories_id(id):
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user:
		print(id)
		cat = Categories.query.filter_by(public_id=id).first_or_404()
		return {
			'id': cat.public_id, 
			'name_categories': cat.name_categories
		}, 201

@app.route('/categories/', methods=['POST'])
@token_required
@cross_origin(supports_credentials=True)
def insert_categories(current_user):
	if not current_user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif current_user.is_admin is True:
		data = request.get_json()
		if not 'name_categories' in data:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Name not given'
			}), 400
		if len(data['name_categories']) < 4 :
			return jsonify({
				'error': 'Bad Request',
				'message': 'Name must be contain minimum of 4 letters'
			}), 400
		cat = Categories(
				name_categories=data['name_categories'],
				public_id=str(uuid.uuid4())
			)
		db.session.add(cat)
		db.session.commit()
		return {
			'id': cat.public_id, 'name_categories': cat.name_categories
		}, 201
	elif current_user.is_admin is False:
		return {
			'message' : 'Your not admin!'
			}

@app.route('/categories/<id>/',  methods=['PUT'])
@cross_origin(supports_credentials=True)
def update_categories(id):
	# decode_var = request.headers.get('Authorization')
	# allow = author_user(decode_var)[0]
	# user = User.query.filter_by(username=allow).first()
	# if not user:
	# 	return {
	# 		'message' : 'Please check your login details and try again.'
	# 	}, 401
	# elif user.is_admin is True :
		data = request.get_json()
		cat = Categories.query.filter_by(public_id=id).first_or_404()
		cat.name_categories = data['name_categories']
		db.session.commit()
		return {
			'message': 'successfully update categories'
		}
	# elif user.is_admin is False:
	# 	return {
	# 		'message' : 'Your not admin! please check again.'
	# 	},401
	# else:
	# 	return {
	# 		'message' : 'UNAUTOHORIZED'
	# 	},401

@app.route('/categories/<id>/', methods=['DELETE'] )
@token_required
@cross_origin(supports_credentials=True)
def delete_categories(current_user, id):
	# if not current_user:
	# 	return {
	# 		'message' : 'Please check your login details and try again.'
	# 	}, 401
	if current_user.is_admin is True :
		cat = Categories.query.filter_by(public_id=id).first_or_404()
		db.session.delete(cat)
		db.session.commit()
		return {
			'success': 'Data deleted successfully'
		},200
	# elif current_user.is_admin is False:
	# 	return {
	# 		'message' : 'Your not admin! please check again.'
	# 	},401
	
#---------------------------------- PRODUCTS

@app.route('/search-products/', methods=['POST'])
def search_product():
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user:
		lis =[]
		data = request.get_json()
		pro = data['product']
		search = "%{}%".format(pro)
		prods = Products.query.filter(Products.name_product.ilike(search)).all()
		if not prods:
			lis.append ({'message' : 'Did not find search'})
			return jsonify(lis),404
		else:
			for x in prods:
				if x.stock > 0:
					lis.append(
						{
							'id': x.public_id, 
							'name': x.name_product,
							'categories': x.categories.name_categories,
							'price': x.price,
							'stock': x.stock,
							'image': x.image
						} 
					)
			return jsonify(lis), 200
		
@app.route('/products/')
@cross_origin(supports_credentials=True)
def get_products():
	# decode_var = request.headers.get('Authorization')
	# allow = author_user(decode_var)[0]
	# user = User.query.filter_by(username=allow).first()
	# if not user:
	# 	return {
	# 		'message' : 'Please check your login details and try again.'
	# 	}, 401
	# elif user:
	return jsonify([
		{
			'id': product.public_id, 
			'name': product.name_product,
			'categories_id': product.categories_id,
			'categories': product.categories.name_categories,
			'price': product.price,
			'stock': product.stock,
			'description': product.description,
			'image': product.image
		} for product in Products.query.order_by(Products.id.desc()).all()
	]),200

@app.route('/products/<id>/')
def get_products_id(id):
	# decode_var = request.headers.get('Authorization')
	# allow = author_user(decode_var)[0]
	# user = User.query.filter_by(username=allow).first()
	# if not user:
	# 	return {
	# 		'message' : 'Please check your login details and try again.'
		# }, 401
	# elif user:
	print(id)
	product = Products.query.filter_by(public_id=id).first_or_404()
	return make_response({
			'id': product.public_id, 
			'name': product.name_product,
			'categories': product.categories.name_categories,
			'price': product.price,
			'stock': product.stock,
			'description': product.description,
			'image': product.image
	}), 200

@app.route('/products/', methods=['POST'])
@token_required
@cross_origin(supports_credentials=True)
def insert_products(current_user):
	# decode_var = request.headers.get('Authorization')
	# allow = author_user(decode_var)[0]
	# user = User.query.filter_by(username=allow).first()
	if not current_user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif current_user.is_admin is True:
		data = request.get_json()
		if not 'name_product' in data:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Name not given'
			}), 400
		if len(data['name_product']) < 4 :
			return jsonify({
				'error': 'Bad Request',
				'message': 'Name must be contain minimum of 4 letters'
			}), 400
		cat = Categories.query.filter_by(id=data['categories_id']).first()
		if not cat:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Invalid categories'
			}), 400
		product = Products(
				name_product=data['name_product'],
				categories_id = cat.id,
				price = data['price'],
				stock=data['stock'],
				description= data['description'],
				image=data['image'],
				public_id=str(uuid.uuid4())
			)
		db.session.add(product)
		db.session.commit()
		return {
			'id': product.public_id, 
			'name': product.name_product,
			'categories': product.categories.name_categories,
			'price': product.price,
			'stock': product.stock,
			'description': product.description,
			'image': product.image
		}, 201
	elif current_user.is_admin is False:
		return {
			'message' : 'Your not admin!'
			}, 401

@app.route('/products/<id>/',  methods=['PUT'])
@cross_origin(supports_credentials=True)
def update_products(id):
	# decode_var = request.headers.get('Authorization')
	# allow = author_user(decode_var)[0]
	# user = User.query.filter_by(username=allow).first()
	# if not user:
		# return {
		# 	'message' : 'Please check your login details and try again.'
		# }, 401
	# elif user.is_admin is True :
		data = request.get_json()
		pro = Products.query.filter_by(public_id=id).first_or_404()
		cat = Categories.query.filter_by(id=data['categories_id']).first()
		if not cat:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Invalid categories'
			}), 400
		if 'name_product' in data:
			pro.name_product = data['name_product']
		if 'description' in data:
			pro.description = data['description']
		if 'categories_id' in data:
			pro.categories_id = cat.id
		if 'stock' in data:
			pro.stock = data['stock']
		if 'image' in data:
			pro.image = data['image']
		if 'price' in data:
			pro.price = data['price']
		db.session.commit()
		return {
			'id': pro.public_id, 
			'name': pro.name_product,
			'categories': pro.categories.name_categories,
			'price': pro.price,
			'stock': pro.stock,
			'description': pro.description,
			'image': pro.image
		}, 201
	# elif user.is_admin is False:
	# 	return {
	# 		'message' : 'Your not admin! please check again.'
	# 	},401
	# else:
	# 	return {
	# 		'message' : 'UNAUTOHORIZED'
	# 	},401

@app.route('/products/<id>/', methods=['DELETE'] )
@cross_origin(supports_credentials=True)
def delete_products(id):
	# decode_var = request.headers.get('Authorization')
	# allow = author_user(decode_var)[0]
	# user = User.query.filter_by(username=allow).first()
	# if not user:
	# 	return {
	# 		'message' : 'Please check your login details and try again.'
	# 	}, 401
	# elif user.is_admin is True :
		pro = Products.query.filter_by(public_id=id).first_or_404()
		db.session.delete(pro)
		db.session.commit()
		return {
			'success': 'Data deleted successfully'
		},200
	# elif user.is_admin is False:
	# 	return {
	# 		'message' : 'Your not admin! please check again.'
	# 	},401

#-------------------------------- CARTS

@app.route('/carts/')
@token_required
def get_carts(current_user):
	if not current_user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif current_user.is_admin is False:
		cart = Cart.query.filter_by(user_id=current_user.id).order_by(Cart.id).all()
		lis = []
		if not cart:
			lis.append({'message' : 'Sorry, no history order'})
			return jsonify(lis),404
		else:
			for x in cart:
				lis.append(
					{
						'id': x.public_id, 
						'user_id': x.user_id, 
						'product_id': x.product_id,
						'name_product': x.product_name,
						'image': x.image,
						'price' : x.price,
						'quantity' : x.quantity,
					} 
				)
			return jsonify(lis),200

@app.route('/carts/', methods=['POST'])
@token_required
@cross_origin(supports_credentials=True)
def add_carts(current_user):
	if not current_user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif current_user.is_admin is False:
		data = request.get_json()
		if not 'name_product' in data:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Name not given'
			}), 400
		pro = Products.query.filter_by(name_product=data['name_product']).first()
		if not pro:
			return jsonify({
				'error': 'Bad Request',
				'message': 'Invalid products'
			}), 400
		cart = Cart(
				user_id=current_user.id,
				product_id = pro.id,
				price = pro.price,
				image = pro.image,
				product_name = data['name_product'],
				quantity=data['quantity'],
				public_id=str(uuid.uuid4())
			)
		db.session.add(cart)
		db.session.commit()
		return {
			'message' : 'success add to carts'
			# 'id': cart.public_id, 
			# 'user_id': cart.name_product,
			# 'categories': cart.categories.name_categories,
			# 'price': cart.price,
			# 'stock': cart.stock,
			# 'description': cart.description,
			# 'image': cart.image
		}, 201

#-------------------------------- ORDERS

@app.route('/order/')
@token_required
def get_order(current_user):
	if not current_user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif current_user.is_admin is False:
		order = Order.query.filter_by(user_id=current_user.id).order_by(Order.date).all()
		lis = []
		if not order:
			lis.append({'message' : 'Sorry, no history order'})
			return jsonify(lis),404
		else:
			for x in order:
				lis.append(
					{
						'id': x.public_id, 
						'name': x.users.name,
						'total_price' : x.total_price,
						'date' : x.date.strftime('%d-%m-%Y'),
						'status' : x.status
					} 
				)
			return jsonify(lis),200
	elif current_user.is_admin is True:
		return jsonify([
		{
			'id': order.id, 
			'user_id': order.user_id,
			'name_user': order.users.name,
			'date': order.date.strftime('%d-%m-%Y'),
			'payment_type': order.payment_type,
			'status': order.status,
			'total_price': order.total_price
		} for order in Order.query.order_by(Order.date.desc()).all()
	]),200

@app.route('/order-detail/')
@token_required
def get_order_detail(current_user):
	if not current_user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif current_user.is_admin is True:
		return jsonify([
		{
			'id': order.id, 
			'order_id': order.order_id,
			'product_id': order.product_id,
			'product_name': order.product_name,
			'quantity': order.quantity,
			'subtotal': order.subtotal,
		} for order in OrderDetail.query.order_by(OrderDetail.id.desc()).all()
	]),200

@app.route('/order/<id>/')
def get_order_id(id):
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user:
		print(id)
		order = Order.query.filter_by(public_id=id).first_or_404()
		return {
				'id': order.public_id, 
				'name': order.users.name,
				'total_price' : order.total_price,
				'date' : order.date,
				'status' : order.status
		}, 201

@app.route('/order/', methods=['POST'])
def add_order():
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user:
		data = request.get_json()
		order =  Order.query.filter_by(status='Active').count()
		if order >= 10:
			return jsonify ({
				'message': 'Please waiting for order'
			}), 503 #Service Unavailable
		today = date.today()
		order = Order(
				user_id = user.id,
				user_name = user.name,
				date = today,
				payment_type=data.get('payment_type', 'Cashless'),
				status= data.get('status', 'Active'),
				total_price= 0,
				public_id=str(uuid.uuid4())
			)
		for entry in range(len(data['order'])):
			if not 'product_id' in data['order'][entry]:
				return {
					'error': 'Bad request',
					'message':'Please input product ID'
				}
			if not 'quantity' in data['order'][entry]:
				return {
					'error': 'Bad request',
					'message': 'Please input quantity'
				}
			pro = Products.query.filter_by(id=data['order'][entry]['product_id']).first()
			if not pro:
				return {
					'error': 'Bad request',
					'message': 'Invalid Id Products'
				}
			if pro.stock == 0:
				return jsonify({
					'message' : pro.name_product+' stock not available'
				}),400
			orderdetail = OrderDetail(
				product_id = pro.id,
				product_name = pro.name_product,
				quantity =  data['order'][entry]['quantity'],
				subtotal= data['order'][entry]['quantity'] * pro.price,
				public_id=str(uuid.uuid4())
			)
			order.orders.append(orderdetail)
			order.total_price += orderdetail.subtotal
			if pro.stock >= orderdetail.quantity :
				pro.stock -= orderdetail.quantity
			else:
				return jsonify({
					'message' : pro.name_product+' stock only '+str(pro.stock) 
				}),400
		db.session.add(order)
		db.session.commit()
		return {
			'id': order.public_id, 
			'name': order.users.name,
			'total_price' : order.total_price,
			'date' : order.date.strftime('%d-%m-%Y'),
			'status' : order.status
		}, 201

@app.route('/order/<id>',  methods=['PUT'])
def update_order(id):
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	order = Order.query.filter_by(public_id=id).first_or_404()
	orderd = OrderDetail.query.filter_by(order_id=order.id).first_or_404()
	pro = Products.query.filter_by(id=orderd.product_id).first_or_404()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user.is_admin is True :
		data = request.get_json()
		order.status = data['status']
		db.session.commit()
		return {
			'message': 'success'
		},202
	elif user.is_admin is False:
		data = request.get_json()
		if 'status' in data:
			order.status = data['status']
		if data['status'] == 'Complete':
			return {
			'message' : 'Edit status complete just for admin'
			}, 401
		if order.status == 'Cancel':
			pro.stock += orderd.quantity
		db.session.commit()
		return {
		'message' : 'Successfuly cancelled order'
		}, 202
	else:
		return {
			'message' : 'UNAUTOHORIZED'
		},401

@app.route('/order/<id>', methods=['DELETE'] )
def delete_order(id):
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user.is_admin is True :
		order = Order.query.filter_by(public_id=id).first_or_404()
		orderd = OrderDetail.query.filter_by(order_id=order.id).first()
		db.session.delete(orderd)
		db.session.delete(order)
		db.session.commit()
		return {
			'success': 'Data deleted successfully'
		},202
	elif user.is_admin is False:
		return {
			'message' : 'Your not admin! please check again.'
		},401

#------------------------------------- REPORTING

@app.route('/most-users/')
@token_required
def get_mostuser(current_user):
	if not current_user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif current_user:
		most = db.engine.execute('''select COUNT(o.user_id) as total_order, u.name from "%s" o left join "%s" u on o.user_id = u.id group by o.user_id, u.name ORDER BY total_order DESC LIMIT 5'''% ("order", "user".strip())) 
		lis = []
		for x in most:
			lis.append({'total_order' :x['total_order'], 'name': x['name']})
		return jsonify(lis),200

@app.route('/most-orders/')
def get_mostorder():
	# decode_var = request.headers.get('Authorization')
	# allow = author_user(decode_var)[0]
	# user = User.query.filter_by(username=allow).first()
	# if not user:
	# 	return {
	# 		'message' : 'Please check your login details and try again.'
	# 	}, 401
	# elif user:
	most = db.engine.execute("select pr.public_id, o.product_id, SUM(o.quantity) as sold, pr.name_product, pr.price, pr.image  from order_detail o  left join products pr on o.product_id = pr.id  group by pr.public_id, o.product_id, pr.name_product, pr.price, pr.image  ORDER BY sold DESC LIMIT 5;")
	lis = []
	for x in most:
		lis.append({'id': x['public_id'], 'total_sold': x['sold'], 'name_product': x['name_product'], 'price': x['price'], 'image':x['image']})
	return jsonify(lis), 200

@app.route('/count-table/')
@token_required
def get_count(current_user):
	if not current_user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif current_user:
		pro = db.engine.execute('select (select count(*) from products) as count_pro,(select count(*) from "user" WHERE is_admin = true) as count_admin, (select count(*) from "user" WHERE is_admin = false) as count_user,(select count(*) from "order") as count_order, (select sum(total_price) from "order") as sum_price') 
		lis = []
		for x in pro:
			lis.append({'pro' :x['count_pro'], 'user': x['count_user'], 'admin': x['count_admin'],'order': x['count_order'], 'price': x['sum_price'] })
		return jsonify(lis),200

@app.route('/sales-graph/')
@token_required
def get_sales_month(current_user):
	if not current_user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif current_user:
		sales = db.engine.execute('''SELECT TO_CHAR(o.date, 'Mon') as mon, COUNT(od.quantity) as sales FROM order_detail od INNER JOIN "order" o ON od.order_id = o.id GROUP BY mon ORDER BY mon;''') 
		lis = []
		for x in sales:
			lis.append({'month' :x['mon'], 'sales': x['sales']})
		return jsonify(lis),200