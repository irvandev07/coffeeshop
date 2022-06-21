import base64
from cgitb import reset
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import date



app = Flask(__name__)
db = SQLAlchemy(app)

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
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	public_id = db.Column(db.String, nullable=False)
	date = db.Column(db.Date, nullable=False)
	payment_type = db.Column(db.String(100), nullable=False)
	status = db.Column(db.String(100), nullable=False)
	total_price = db.Column(db.Integer, nullable=False)
	orders = db.relationship('OrderDetail', backref='orders', lazy=True, cascade="all, delete")

	def repr(self):
		return f'Order <{self.status}>'	

class OrderDetail(db.Model):
	id = db.Column(db.Integer, primary_key=True, index=True)
	order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
	product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
	public_id = db.Column(db.String, nullable=False)
	quantity = db.Column(db.Integer, nullable=False)
	subtotal = db.Column(db.Integer, nullable=False)

	def repr(self):
		return f'Order <{self.status}>'	

# db.create_all()
# db.session.commit()

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
def register_user():
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
		}),200

@app.route('/users/<id>/', methods=['DELETE'] )
def delete_user(id):
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user.is_admin is True :
		user = User.query.filter_by(public_id=id).first_or_404()
		db.session.delete(user)
		db.session.commit()
		return {
			'success': 'Data deleted successfully'
		},200
	elif user.is_admin is False:
		return {
			'message' : 'Your not admin! please check again.'
		},401

#---------------------------------- CATEGORIES

@app.route('/categories/')
def get_category():
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
				'id': categories.public_id, 
				'name': categories.name_categories
			} for categories in Categories.query.all()
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
			'name': cat.name_categories
		}, 201

@app.route('/categories/', methods=['POST'])
def insert_categories():
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user.is_admin is True:
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
			'id': cat.public_id, 'name': cat.name_categories
		}, 201
	elif user.is_admin is False:
		return {
			'message' : 'Your not admin!'
			}

@app.route('/categories/<id>',  methods=['PUT'])
def update_categories(id):
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user.is_admin is True :
		data = request.get_json()
		cat = Categories.query.filter_by(public_id=id).first_or_404()
		cat.name_categories = data['name_categories']
		db.session.commit()
		return {
			'message': 'success'
		}
	elif user.is_admin is False:
		return {
			'message' : 'Your not admin! please check again.'
		},401
	else:
		return {
			'message' : 'UNAUTOHORIZED'
		},401

@app.route('/categories/<id>/', methods=['DELETE'] )
def delete_categories(id):
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user.is_admin is True :
		cat = Categories.query.filter_by(public_id=id).first_or_404()
		db.session.delete(cat)
		db.session.commit()
		return {
			'success': 'Data deleted successfully'
		},200
	elif user.is_admin is False:
		return {
			'message' : 'Your not admin! please check again.'
		},401
	
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
		prods = Products.query.filter(Products.name_product.like(search)).all()
		if not prods:
			lis.append ({'message' : 'Did not find search'})
			return jsonify(lis),200
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
			return jsonify(lis)
		
@app.route('/products/')
def get_products():
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
				'id': product.public_id, 
				'name': product.name_product,
				'categories': product.categories.name_categories,
				'price': product.price,
				'stock': product.stock,
				'description': product.description,
				'image': product.image

			} for product in Products.query.all()
		]),200

@app.route('/products/<id>/')
def get_products_id(id):
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user:
		print(id)
		product = Products.query.filter_by(public_id=id).first_or_404()
		return {
				'id': product.public_id, 
				'name': product.name_product,
				'categories': product.categories.name_categories,
				'price': product.price,
				'stock': product.stock,
				'description': product.description,
				'image': product.image
		}, 201

@app.route('/products/', methods=['POST'])
def insert_products():
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user.is_admin is True:
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
		cat = Categories.query.filter_by(name_categories=data['name_categories']).first()
		if not cat:
			return {
				'error': 'Bad request',
				'message': 'Invalid Name Categories'
			}
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
			'message' : 'success',
			'id': product.public_id, 
			'name': product.name_product,
			'categories': product.categories.name_categories,
			'price': product.price,
			'stock': product.stock,
			'description': product.description,
			'image': product.image
		}, 201
	elif user.is_admin is False:
		return {
			'message' : 'Your not admin!'
			}

@app.route('/products/<id>',  methods=['PUT'])
def update_products(id):
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user.is_admin is True :
		data = request.get_json()
		pro = Products.query.filter_by(public_id=id).first_or_404()
		pro.stock += data['stock']
		db.session.commit()
		return {
			'message': 'success update'
		}
	elif user.is_admin is False:
		return {
			'message' : 'Your not admin! please check again.'
		},401
	else:
		return {
			'message' : 'UNAUTOHORIZED'
		},401

@app.route('/products /<id>/', methods=['DELETE'] )
def delete_products(id):
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user.is_admin is True :
		pro = Products.query.filter_by(public_id=id).first_or_404()
		db.session.delete(pro)
		db.session.commit()
		return {
			'success': 'Data deleted successfully'
		},200
	elif user.is_admin is False:
		return {
			'message' : 'Your not admin! please check again.'
		},401

#-------------------------------- ORDERS

@app.route('/order/')
def get_order():
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user:
		order = Order.query.filter_by(user_id=user.id).order_by(Order.date.desc()).all()
		lis = []
		if not order:
			lis.append({'message' : 'Sorry, no history order'})
			return jsonify(lis),200
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
			}), 400
		today = date.today()
		order = Order(
				user_id = user.id,
				date = today,
				payment_type=data.get('payment_type', 'Cashless'),
				status= data.get('status', 'Active'),
				total_price= 0,
				public_id=str(uuid.uuid4())
			)
		if not 'quantity' in data:
			return {
				'error': 'Bad request',
				'message': 'Invalid Quantity'
			}
		for x in range(len(data['name_product'])):
			pro = Products.query.filter_by(name_product=data['name_product'][x]).first()
			if not pro:
				return {
					'error': 'Bad request',
					'message': 'Invalid Name Products'
				}
			if pro.stock == 0:
				return jsonify ({
					'message': 'Product not available'
				}), 400
			orderdetail = OrderDetail(
				product_id = pro.id,
				quantity =  data['quantity'][x],
				subtotal= data['quantity'][x] * pro.price,
				public_id=str(uuid.uuid4())
			)
			order.orders.append(orderdetail)
			order.total_price += orderdetail.subtotal
			if pro.stock > 0 :
				pro.stock -= orderdetail.quantity
		db.session.add(order)
		db.session.commit()
		return {
			'id': order.public_id, 
			'name': order.users.name,
			'total_price' : order.total_price,
			'date' : order.date,
			'status' : order.status
		}, 201

@app.route('/order/<id>',  methods=['PUT'])
def update_order(id):
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	order = Order.query.filter_by(public_id=id).first_or_404()
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
		}
	elif user.is_admin is False:
		data = request.get_json()
		order.status = data['status']
		if data['status'] == 'Complete':
			return {
			'message' : 'Edit status complete just for admin'
			}, 401
		db.session.commit()
		return {
			'message': 'success'
		}
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
		},200
	elif user.is_admin is False:
		return {
			'message' : 'Your not admin! please check again.'
		},401


#------------------------------------- REPORTING

@app.route('/most-users/')
def get_mostuser():
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user:
		most = db.engine.execute('''select COUNT(o.user_id) as total_order, u.name from "%s" o left join "%s" u on o.user_id = u.id group by o.user_id, u.name ORDER BY total_order DESC LIMIT 5'''% ("order", "user".strip())) 
		lis = []
		for x in most:
			lis.append({'total_order' :x['total_order'], 'name': x['name']})
		return jsonify(lis)

@app.route('/most-orders/')
def get_mostorder():
	decode_var = request.headers.get('Authorization')
	allow = author_user(decode_var)[0]
	user = User.query.filter_by(username=allow).first()
	if not user:
		return {
			'message' : 'Please check your login details and try again.'
		}, 401
	elif user:
		most = db.engine.execute("select o.product_id, SUM(o.quantity) as qt, pr.name_product from order_detail o left join products pr on o.product_id = pr.id group by o.product_id, pr.name_product ORDER BY qt DESC LIMIT 5;")
		lis = []
		for x in most:
			lis.append({'total_sold': x['qt'], 'name': x['name_product']})
		return jsonify(lis)