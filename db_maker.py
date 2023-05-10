from tool_sharing_website import db, app
from tool_sharing_website.models import User, Tool, Message, Review, Report, datetime, CartItem, Order, Dispute
from tool_sharing_website import stripe
from tool_sharing_website.maps import findAddress, findCoords, getStreetID

# This file is used to create the database and populate it with some dummy data. It is not used in the actual website, but it is useful for testing purposes.

with app.app_context():
    db.drop_all()
    db.create_all()
    #stripe.Product.delete("prod_JZ1Z1Z1Z1Z1Z1Z")
    #stripe.Account.delete("acct_1Mr02nCrf3y5ScqE")
    #stripe.PaymentIntent.create(amount=500, currency="gbp", payment_method="pm_card_visa")
    # stripe.Account.delete("acct_1MwSAzEOdh3cF1Ym")
    # stripe.Account.delete("acct_1N3GVPCdNjEo4owV")
    user1 = User(username="user1", email="user1@email.com", password="password", address="4 Blaenclydach Street, CF11 7BB", is_verified=True, is_banned=False, stripe_customer_id="cus_NS8AWGnHK3xJSh", stripe_connect_id="acct_1Mr4Pu2RevaUSZN6")
    user2 = User(username="user2", email="user2@email.com", password="password", address="4 Blaenclydach Street CF11 7BB", is_verified=True, is_banned=False, stripe_customer_id="cus_NS8A2D92TqNiOO", stripe_connect_id="acct_1Mr4WcCry81PcqQ0")
    user3 = User(username="user3", email="user3@email.com", password="password", address="12 Blaise Place CF11 6JR", is_verified=True, is_banned=False, stripe_customer_id="cus_NS8A2PApsxmFVy", stripe_connect_id="acct_1Mr4ZQCWWkQcP8zk")
    user4 = User(username="user4", email="user4@email.com", password="password", address="30 Oakfield Road NP20 4LX", is_verified=True, is_banned=False, stripe_customer_id="cus_NczpYdsSJcFNpz", stripe_connect_id="acct_1MrjoVCW9MSZoTkp")
    user5 = User(username="user5", email="user5@email.com", password="password", address="35 Kincraig Street CF24 3HW", is_verified=True, is_banned=False, stripe_customer_id="cus_Nczua4H83i4nmq", stripe_connect_id="acct_1Mrju1E7hJEaRZLN")
    user6 = User(username="user6", email="user6@email.com", password="password", address="50 Coburn Street CF24 4BS", is_verified=True, is_banned=False, stripe_customer_id="cus_Nd021Bq67mpiK6", stripe_connect_id="acct_1Mrk1CCo6JOwbOtV")
    user7 = User(username="user7", email="user7@email.com", password="password", address="40 Australia Rd CF14 3DB", is_verified=True, is_banned=False, stripe_customer_id="cus_Nd0CHyncRX177o", stripe_connect_id="acct_1MrkBVCiudPwronf")
    user8 = User(username="user8", email="user8@email.com", password="password", address="24 Farmleigh CF3 3LE", is_verified=True, is_banned=False, stripe_customer_id="cus_Nd0MLzFYF6J25L", stripe_connect_id="acct_1MrkLAELEIpz5PjO")
    user9 = User(username="user9", email="user9@email.com", password="password", address="37 Burnaby St CF24 2JX", is_verified=True, is_banned=False, stripe_customer_id="cus_Nd0PiykkdvGZ3S", stripe_connect_id="acct_1MrkNQChl4lsT9ll")
    user10 = User(username="user10", email="user10@email.com", password="password", address="36 Daniel St CF24 4NY", is_verified=True, is_banned=True, stripe_customer_id="cus_Nd0SMERRfuEkhk", stripe_connect_id="acct_1MrkQWED1vtkXo9r")
    user11 = User(username="user11", email="user11@email.com", password="password", address="1 Woodville Road CF24 4DW", is_verified=False, is_banned=False, stripe_customer_id="cus_NhrwB6R8CEzWys", stripe_connect_id="acct_1MwSAzEOdh3cF1Ym")
    admin = User(username="admin", email="admin@email.com", password="password", address="10 Downing St SW1A 2AB", is_verified=True, is_banned=False, is_admin=True, stripe_customer_id="cus_NS8A6jsMx86GAp", stripe_connect_id="acct_1Mr4bLCdRbAxir5W")

    rake = Tool(name="Rake", description="An implement consisting of a pole with a toothed crossbar or fine tines at the end, used especially for drawing together cut grass or smoothing loose soil or gravel.", owner=1, borrower=None, address="4 Blaenclydach Street CF11 7BB", deposit=1000, is_available=True, high_risk=False, rental_period=9, image_path="rake.jpg", category="garden", stripe_id="prod_JZ1Z1Z1Z1Z1Z1Z", public_address="Blaenclydach St, Cardiff CF11 7BB, UK", lat=51.4709412, lng=-3.1830723)
    shovel = Tool(name="Shovel", description="A shovel is a tool used for digging, lifting, and moving bulk materials, such as soil, coal, gravel, snow, sand, or ore.", owner=1, borrower=None, address="4 Blaenclydach Street CF11 7BB", deposit=1000, is_available=True, high_risk=False, rental_period=9, category="garden", stripe_id="prod_JZ2Z2Z2Z2Z2Z2Z", public_address="Blaenclydach St, Cardiff CF11 7BB, UK", lat=51.4709412, lng=-3.1830723, image_path="shovel.jpg")
    circular_saw = Tool(name="Circular saw", description="A circular saw is a power-saw using a toothed or abrasive disc or blade to cut different materials using a rotary motion spinning around an arbor.", owner=3, borrower=None, address="12 Blaise Place CF11 6JR", deposit=5000, is_available=True, high_risk=True, rental_period=9, category="garden", stripe_id="prod_JZ3Z3Z3Z3Z3Z3", public_address="Blaise Place, Cardiff CF11 6JR, UK", lat=51.4672159, lng=-3.1948531, image_path="circularsaw.jpg")
    
    #stripe.Product.create(name="Rake", description="An implement consisting of a pole with a toothed crossbar or fine tines at the end, used especially for drawing together cut grass or smoothing loose soil or gravel.", default_price_data={"currency": "gbp", "unit_amount_decimal": 1000}, id="prod_JZ1Z1Z1Z1Z1Z1Z")
    #stripe.Product.create(name="Shovel", description="A shovel is a tool used for digging, lifting, and moving bulk materials, such as soil, coal, gravel, snow, sand, or ore.", default_price_data={"currency": "gbp", "unit_amount_decimal": 1000}, id="prod_JZ2Z2Z2Z2Z2Z2Z")
    #stripe.Product.create(name="Circular saw", description="A circular saw is a power-saw using a toothed or abrasive disc or blade to cut different materials using a rotary motion spinning around an arbor.", default_price_data={"currency": "gbp", "unit_amount_decimal": 5000}, id="prod_JZ3Z3Z3Z3Z3Z3")

    # rake2 = Tool(name="Pink Rake", description="An implement consisting of a pole with a toothed crossbar or fine tines at the end, used especially for drawing together cut grass or smoothing loose soil or gravel.", owner=1, borrower=None, address="4 Blaenclydach Street, CF11 7BB", deposit=5000, is_available=True, high_risk=True, rental_period=2, image_path="pinkrake.jpg", category="garden", stripe_id="prod_JZ5Z5Z5Z5Z5Z5Z", public_address="Blaenclydach St, Cardiff CF11 7BB, UK")
    # stripe.Product.create(name="Pink Rake", description="An implement consisting of a pole with a toothed crossbar or fine tines at the end, used especially for drawing together cut grass or smoothing loose soil or gravel.", default_price_data={"currency": "gbp", "unit_amount_decimal": 5000}, id="prod_JZ5Z5Z5Z5Z5Z5Z")
    axe = Tool(name="Axe", description="An axe is an implement that has been used for millennia to shape, split and cut wood; to harvest timber; as a weapon; and as a ceremonial or heraldic symbol.", owner=4, borrower=None, address="30 Oakfield Road NP20 4LX", deposit=2350, is_available=True, high_risk=True, rental_period=5, category="garden", stripe_id="prod_JZ6Z6Z6Z6Z6Z6Z", public_address="Oakfield Rd, Newport NP20 4LX, UK", lat=51.58579169999999, lng=-3.0101482, image_path="axe.jpg")
    # stripe.Product.create(name="Axe", description="An axe is an implement that has been used for millennia to shape, split and cut wood; to harvest timber; as a weapon; and as a ceremonial or heraldic symbol.", default_price_data={"currency": "gbp", "unit_amount_decimal": 2350}, id="prod_JZ6Z6Z6Z6Z6Z6Z")
    hammer = Tool(name="Hammer", description="A hammer is a tool or device that delivers a blow to an object.", owner=5, borrower=None, address="35 Kincraig Street CF24 3HW", deposit=550, is_available=True, high_risk=False, rental_period=14, category="garden", stripe_id="prod_JZ7Z7Z7Z7Z7Z7Z", public_address="Kincraig St, Cardiff CF24 3HW, UK", lat=51.4908124, lng=-3.1688227, image_path="hammer.jpg")
    # stripe.Product.create(name="Hammer", description="A hammer is a tool or device that delivers a blow to an object.", default_price_data={"currency": "gbp", "unit_amount_decimal": 550}, id="prod_JZ7Z7Z7Z7Z7Z7Z")
    drill = Tool(name="Drill", description="A drill is a tool fitted with a cutting tool attachment or driving tool attachment, usually a drill bit or driver bit, used for boring holes in various materials or fastening various materials together with the use of fasteners.", owner=6, borrower=None, address="50 Coburn Street CF24 4BS", deposit=2495, is_available=True, high_risk=True, rental_period=7, category="garden", stripe_id="prod_JZ8Z8Z8Z8Z8Z8Z", public_address="Coburn St, Cardiff CF24 4BS, UK", lat=51.49035319999999, lng=-3.1742844, image_path="drill.jpg")
    # stripe.Product.create(name="Drill", description="A drill is a tool fitted with a cutting tool attachment or driving tool attachment, usually a drill bit or driver bit, used for boring holes in various materials or fastening various materials together with the use of fasteners.", default_price_data={"currency": "gbp", "unit_amount_decimal": 2495}, id="prod_JZ8Z8Z8Z8Z8Z8Z")
    air_fryer = Tool(name="Air Fryer", description="An air fryer is a kitchen appliance that uses hot air in combination with high-speed air circulation (rapid hot air) to cook food.", owner=7, borrower=None, address="40 Australia Rd CF14 3DB", deposit=6750, is_available=True, high_risk=False, rental_period=10, category="kitchen", stripe_id="prod_JZ9Z9Z9Z9Z9Z9Z", public_address="Australia Rd, Cardiff CF14 3DB, UK", lat=51.5014615, lng=-3.1908934, image_path="airfryer.jpg")
    # stripe.Product.create(name="Air Fryer", description="An air fryer is a kitchen appliance that uses hot air in combination with high-speed air circulation (rapid hot air) to cook food.", default_price_data={"currency": "gbp", "unit_amount_decimal": 6750}, id="prod_JZ9Z9Z9Z9Z9Z9Z")
    blender = Tool(name="Blender", description="A blender is a kitchen and laboratory appliance used to mix, purée, or emulsify food and other substances.", owner=8, borrower=None, address="24 Farmleigh CF3 3LE", deposit=1500, is_available=True, high_risk=False, rental_period=3, category="kitchen", stripe_id="prod_JZ10Z10Z10Z10Z10Z", public_address="Farmleigh, Cardiff CF3 3LE, UK", lat=51.5086927, lng=-3.1260949, image_path="blender.jpg")
    # stripe.Product.create(name="Blender", description="A blender is a kitchen and laboratory appliance used to mix, purée, or emulsify food and other substances.", default_price_data={"currency": "gbp", "unit_amount_decimal": 1500}, id="prod_JZ10Z10Z10Z10Z10Z")
    toaster = Tool(name="Toaster", description="A toaster is an electric small appliance designed to toast slices of bread by exposing them to radiant heat, thus converting them into a form that is palatable and easier to digest.", owner=9, borrower=None, address="37 Burnaby St CF24 2JX", deposit=500, is_available=True, high_risk=False, rental_period=10, category="kitchen", stripe_id="prod_JZ11Z11Z11Z11Z11Z", public_address="Burnaby St, Cardiff CF24 2JX, UK", lat=51.4836098, lng=-3.1506508, image_path="toaster.jpg")
    # stripe.Product.create(name="Toaster", description="A toaster is an electric small appliance designed to toast slices of bread by exposing them to radiant heat, thus converting them into a form that is palatable and easier to digest.", default_price_data={"currency": "gbp", "unit_amount_decimal": 500}, id="prod_JZ11Z11Z11Z11Z11Z")
    kettle = Tool(name="Kettle", description="A kettle is a type of pot, traditionally made of metal, with a lid, a small spout for pouring, and a handle.", owner=10, borrower=None, address="36 Daniel St CF24 4NY", deposit=450, is_available=True, high_risk=False, rental_period=4, category="kitchen", stripe_id="prod_JZ12Z12Z12Z12Z12Z", public_address="Daniel St, Cardiff CF24 4NY, UK", lat=51.4962241, lng=-3.1779503, image_path="kettle.jpg")
    # stripe.Product.create(name="Kettle", description="A kettle is a type of pot, traditionally made of metal, with a lid, a small spout for pouring, and a handle.", default_price_data={"currency": "gbp", "unit_amount_decimal": 450}, id="prod_JZ12Z12Z12Z12Z12Z")


    review1 = Review(tool_id=1, reviewer=2, reviewee=1, rating=5, comments="Good")
    review2 = Review(tool_id=1, reviewer=1, reviewee=2, rating=5, comments="Good product, would buy from user2 again")
    #Auto-generated reviews
    review3 = Review(tool_id=2, reviewer=3, reviewee=1, rating=4, comments="The tool was in good condition")
    review4 = Review(tool_id=2, reviewer=5, reviewee=3, rating=3, comments="The tool was okay, but could have been better")
    review5 = Review(tool_id=3, reviewer=7, reviewee=2, rating=5, comments="Great tool, highly recommend")
    review6 = Review(tool_id=3, reviewer=9, reviewee=4, rating=4, comments="Good tool, but a bit pricey")
    review7 = Review(tool_id=4, reviewer=2, reviewee=1, rating=2, comments="The tool was not in good condition")
    review8 = Review(tool_id=4, reviewer=1, reviewee=3, rating=1, comments="Do not recommend this tool or user")
    review9 = Review(tool_id=5, reviewer=6, reviewee=2, rating=5, comments="Excellent tool, worked perfectly")
    review10 = Review(tool_id=5, reviewer=8, reviewee=4, rating=4, comments="Good tool, but a bit difficult to use")
    review11 = Review(tool_id=6, reviewer=3, reviewee=1, rating=3, comments="The tool was average")
    review12 = Review(tool_id=6, reviewer=5, reviewee=3, rating=3, comments="The tool was okay, not the best")
    review13 = Review(tool_id=7, reviewer=7, reviewee=2, rating=4, comments="Decent tool, did the job")
    review14 = Review(tool_id=8, reviewer=9, reviewee=4, rating=5, comments="Excellent tool, very useful")
    review15 = Review(tool_id=10, reviewer=4, reviewee=1, rating=4, comments="Good tool, no complaints")

    message1 = Message(sender=1, receiver=2,  message="Hello, how are you?", timestamp=datetime(2022, 1, 1, 1, 1, 0))
    message2 = Message(sender=2, receiver=1, message="Hello, I am good, how are you?", timestamp=datetime(2022, 1, 1, 1, 1, 1))
    message3 = Message(sender=1, receiver=2, message="I am good, thanks for asking", timestamp=datetime(2022, 1, 1, 1, 1, 2))
    message4 = Message(sender=2, receiver=1, message="No problem, I am glad to hear that", timestamp=datetime(2022, 1, 1, 1, 1, 3))
    #Auto-generated messages
    message5 = Message(sender=1, receiver=5, message="Hi there, I'm interested in borrowing your hammer. When would be a good time for me to come by and pick it up?", timestamp=datetime(2022, 3, 1, 10, 0, 0))
    message6 = Message(sender=5, receiver=1, message="Hi, I'm available tomorrow after 3pm. Does that work for you?", timestamp=datetime(2022, 3, 1, 10, 5, 0))
    message7 = Message(sender=1, receiver=5, message="Yes, that works for me. What's your address?", timestamp=datetime(2022, 3, 1, 10, 10, 0))
    message8 = Message(sender=5, receiver=1, message="123 Main Street. See you tomorrow at 3pm!", timestamp=datetime(2022, 3, 1, 10, 15, 0))

    message9 = Message(sender=3, receiver=4, message="Hi, I'm interested in borrowing your lawn mower. Is it available?", timestamp=datetime(2022, 3, 2, 14, 0, 0))
    message10 = Message(sender=4, receiver=3, message="Yes, it's available. When do you need it?", timestamp=datetime(2022, 3, 2, 14, 5, 0))
    message11 = Message(sender=3, receiver=4, message="I was hoping to borrow it this weekend. Is that possible?", timestamp=datetime(2022, 3, 2, 14, 10, 0))
    message12 = Message(sender=4, receiver=3, message="Sure, that works for me. Can you pick it up on Saturday morning?", timestamp=datetime(2022, 3, 2, 14, 15, 0))
    message13 = Message(sender=3, receiver=4, message="Yes, Saturday morning works for me. What's your address?", timestamp=datetime(2022, 3, 2, 14, 20, 0))
    message14 = Message(sender=4, receiver=3, message="It's 456 Oak Street. See you Saturday at 9am!", timestamp=datetime(2022, 3, 2, 14, 25, 0))

    message15 = Message(sender=5, receiver=6, message="Hi, I'm interested in borrowing your drill. Can I pick it up tomorrow?", timestamp=datetime(2022, 3, 3, 11, 0, 0))
    message16 = Message(sender=6, receiver=5, message="Sure, that works. What time tomorrow?", timestamp=datetime(2022, 3, 3, 11, 5, 0))
    message17 = Message(sender=5, receiver=6, message="How about 2pm?", timestamp=datetime(2022, 3, 3, 11, 10, 0))
    message18 = Message(sender=6, receiver=5, message="That works for me. My address is 789 Maple Avenue.", timestamp=datetime(2022, 3, 3, 11, 15, 0))
    message19 = Message(sender=5, receiver=6, message="Great, see you tomorrow at 2pm!", timestamp=datetime(2022, 3, 3, 11, 20, 0))

    report1 = Report(reporter=1, reported=10, description="Offensive language", timestamp=datetime(2022, 1, 1, 1, 1, 4), handled=True)
    report2 = Report(reporter=2, reported=3, description="Spam in chat", timestamp=datetime(2022, 1, 1, 1, 1, 5), handled=False)

    db.session.add_all([
        user1,user2,user3, user4, user5, user6, user7, user8, user9, user10, user11,
        admin,
        rake,shovel,circular_saw,axe,hammer,drill,air_fryer,blender,toaster,kettle,
        review1,review2, review3, review4, review5, review6, review7, review8, review9, review10, review11, review12, review13, review14, review15,
        message1,message2,message3,message4, message5,message6,message7,message8, message9,message10,message11,message12,message13,message14, message15,message16,message17,message18,message19,
        report1,report2,
        ])
    db.session.commit()

    ######Add lat and lng to tools automatically########
    ######To use, set the nullable=False in lat and lng in models.py, then add your tool without lat and lng########
    # tools = Tool.query.all()
    # for tool in tools:
    #     tool_place_id = findAddress(tool.address)[0]
    #     road_place_id = getStreetID(tool_place_id)
    #     lat = findCoords(road_place_id)[0]
    #     lng = findCoords(road_place_id)[1]
    #     tool.lat = lat
    #     tool.lng = lng
    #     print (tool.name, tool.lat, tool.lng)

    # db.session.commit()
