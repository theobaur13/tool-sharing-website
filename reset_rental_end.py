from tool_sharing_website import db, app
from tool_sharing_website.models import User, Tool, Order, Review, Message, Report, Dispute, datetime

tool_name = input("Tool name: ")
print (tool_name)
with app.app_context():
    tool = Tool.query.filter_by(name=tool_name).first()
    order = Order.query.filter_by(tool=tool.id).first()
    order.rental_end = datetime.utcnow()
    db.session.commit()
