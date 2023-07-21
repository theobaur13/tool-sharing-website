from tool_sharing_website import db, login_manager
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(60), nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    is_banned = db.Column(db.Boolean, nullable=False, default=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    sent_messages = db.relationship('Message', backref='sent', lazy=True, foreign_keys='Message.sender')
    received_messages = db.relationship('Message', backref='received', lazy=True, foreign_keys='Message.receiver')
    left_reviews = db.relationship('Review', backref='reviews_left', lazy=True, foreign_keys='Review.reviewer')
    received_reviews = db.relationship('Review', backref='reviews_received', lazy=True, foreign_keys='Review.reviewee')
    left_reports = db.relationship('Report', backref='reports_left', lazy=True, foreign_keys='Report.reporter')
    received_reports = db.relationship('Report', backref='reports_received', lazy=True, foreign_keys='Report.reported')
    listed_tools = db.relationship('Tool', backref='tools_listed', lazy=True, foreign_keys='Tool.owner')
    borrowed_tools = db.relationship('Tool', backref='tools_borrowed', lazy=True, foreign_keys='Tool.borrower')
    ordered_tools = db.relationship('Order', backref='orders_made_by_user', lazy=True, foreign_keys='Order.orderer')
    received_orders = db.relationship('Order', backref='orders_received', lazy=True, foreign_keys='Order.owner')
    stripe_customer_id = db.Column(db.String(128), nullable=False)
    #cards_saved = db.relationship('StripePaymentMethods', backref='saved_cards', lazy=True, foreign_keys='StripePaymentMethods.user_id')
    stripe_connect_id = db.Column(db.String(128), nullable=False)
    disputed_as_orderer = db.relationship('Dispute', backref='disputed_as_borrower', lazy=True, foreign_keys='Dispute.orderer')
    disputed_as_owner = db.relationship('Dispute', backref='disputed_as_owner_', lazy=True, foreign_keys='Dispute.owner')

    def __repr__(self):
        return f"Repr: User('{self.username}', '{self.email}')"

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.hashed_password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.hashed_password, password)

class Tool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(120), nullable=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    borrower = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    address = db.Column(db.String(60), nullable=False)
    deposit = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, nullable=False, default=False)
    high_risk = db.Column(db.Boolean, nullable=False, default=False)
    rental_period = db.Column(db.Integer, nullable=False)
    image_path = db.Column(db.String(60), nullable=True, default='default.jpg')
    category = db.Column(db.String(60), nullable=True)
    stripe_id = db.Column(db.String(60), nullable=False)
    orders = db.relationship('Order', backref='orders_made', lazy=True, foreign_keys='Order.tool')
    disputes = db.relationship('Dispute', backref='disputes_made', lazy=True, foreign_keys='Dispute.tool')
    reviews = db.relationship('Review', backref='reviews_made', lazy=True, foreign_keys='Review.tool_id')
    public_address = db.Column(db.String(60), nullable=False)
    lat = db.Column(db.Float, nullable=False) #latitude of street of tool
    lng = db.Column(db.Float, nullable=False) #longitude of street of tool

    def __repr__(self):
        return f"Repr: Tool('{self.name}', '{self.description}', '{self.owner}', '{self.borrower}', '{self.deposit}', '{self.rental_period}', '{self.image_path}', '{self.is_available}', '{self.address}')"

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(60), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True) #Shouldn't be nullable but for now it is
    tool_id = db.Column(db.Integer, db.ForeignKey('tool.id'), nullable=False)
    reviewer = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewee = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.Column(db.String(60), nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reported = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(60), nullable=False)
    handled = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Repr: Report('{self.description}', '{self.reported}', '{self.reporter}', '{self.timestamp}')"

#TODO: Proper relationships between cart item, user and tool
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    tool_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Repr: CartItem('{self.user_id}', '{self.tool_id}', '{self.is_checked_out}', '{self.timestamp}')"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orderer = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tool = db.Column(db.Integer, db.ForeignKey('tool.id'), nullable=False)
    rental_start = db.Column(db.DateTime, nullable=False)
    rental_end = db.Column(db.DateTime, nullable=False)
    is_accepted = db.Column(db.Boolean, nullable=False, default=False)
    reviews = db.relationship('Review', backref='reviews_made_on_order', lazy=True, foreign_keys='Review.order')

class Dispute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orderer = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tool = db.Column(db.Integer, db.ForeignKey('tool.id'), nullable=False)
    description = db.Column(db.String(60), nullable=True)
    handled = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

#This is no longer required, might be nice to implement later
# class StripePaymentMethods(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     payment_method_id = db.Column(db.String(60), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
