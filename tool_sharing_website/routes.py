from tool_sharing_website import app, db, os
from flask import render_template, url_for, flash, redirect, request, abort, session
from tool_sharing_website.models import User, Tool, Message, Review, Report, check_password_hash, datetime, timedelta, CartItem, Order, Dispute
from tool_sharing_website.forms import RegistrationForm, LoginForm, CreateListingForm, ReportForm, BanForm, RemoveListingForm, CheckoutForm, MessageForm, SearchForm, FilterForm, DistForm, ConfirmForm, EditListingForm, DisputeForm, ReturnDepositForm, ChangeAddressForm, ReviewForm
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from tool_sharing_website import mailer
from sqlalchemy import func, or_, and_, not_
from keys import api_key
import re
from tool_sharing_website.maps import distance, findAddress, pureDistance,  findCoords, getStreetID, getAddressName
from tool_sharing_website import stripe
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

s = URLSafeTimedSerializer("SECRET_KEY_CHANGE_ME")

@app.route("/", methods=["GET", "POST"])
def home():
    tools = Tool.query.filter_by(is_available=True).all()   
    users = User.query.all()    
    distances = {}

    #Initialise search parameters from URL and autofill forms
    if request.args.get("search"):
        # /?search=term+current_searchloc+raw_current_searchloc+search_radius+current_sort+current_dist
        search = request.args.get("search").split("+")
        search_term = search[0]
        current_searchloc = search[1]
        raw_current_searchloc = search[2]
        search_radius = search[3]
        current_sort = search[4]
        current_dist = search[5]

        form_autofill_object = {"searchterm": search_term, "searchterm2": raw_current_searchloc}
        form2_autofill_object = {"select2": current_sort}
        form3_auto_fill_object = {"select3": current_dist}

        form = SearchForm(data=form_autofill_object)
        form2 = FilterForm(data=form2_autofill_object)
        form3 = DistForm(data=form3_auto_fill_object)
    
    #If no search params in URL then initialise to default and autofill forms
    else:
        search_term = ""
        current_searchloc = ""
        raw_current_searchloc = ""
        search_radius = 999999
        current_sort = "none1"
        current_dist = "unlimited"

        form_autofill_object = {"searchterm": search_term, "searchterm2": raw_current_searchloc}
        form2_autofill_object = {"select2": current_sort}
        form3_auto_fill_object = {"select3": current_dist}

        form = SearchForm(data=form_autofill_object)
        form2 = FilterForm(data=form2_autofill_object)
        form3 = DistForm(data=form3_auto_fill_object)

    #Change the search parameters on submit and redirect back to homepage
    if form.validate_on_submit() or form2.validate_on_submit() or form3.validate_on_submit():
        search_term = form.searchterm.data
        raw_current_searchloc = form.searchterm2.data
        found_addresses = findAddress(raw_current_searchloc)
        if found_addresses:
            current_searchloc = found_addresses[0]
        else:
            current_searchloc = ""
            flash ("No address found", "danger")
        current_sort = form2.select2.data
        current_dist = form3.select3.data
        if current_dist == "unlimited":
            search_radius = 999999
        else:
            search_radius = float(current_dist)
        return redirect(url_for("home", search=f"{search_term}+{current_searchloc}+{raw_current_searchloc}+{search_radius}+{current_sort}+{current_dist}"))

    #Set distance values
    if current_searchloc != "":
        for tool in tools:
            print (tool.name)
            distances[tool.id] = distance(tool.address, current_searchloc)[0].split(" ")[0]
    
    #Sort the results
    theTools = sortResults(current_sort, search_term , current_searchloc, search_radius)

    #If there arent any search parameters, return the homepage
    if not request.args.get("search"):
        return render_template("home.html", title="Home", tools=tools, users=users, form=form, form3 = form3, filterform = form2, distances=distances)

    #If there are search parameters, return the search results page
    return render_template("listing_search_result.html", title="Home", tools=theTools, users=users, form=form, form3 = form3, form2 = form2, distances=distances, theTools = theTools)
            
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def post(post_id):
    form = RemoveListingForm()
    tool = Tool.query.get_or_404(post_id)
    if form.validate_on_submit():
        if current_user.id == tool.owner or current_user.is_admin: 
            db.session.delete(tool)
            db.session.commit()
            flash(f"Listing removed", "success")
            return redirect(url_for("home"))
    place_id = findAddress(tool.address)[0]
    street = getStreetID(place_id)
    street_coords = findCoords(street)
    return render_template("post.html", title=tool.name, tool=tool, form=form, api_key=api_key, street=street, street_coords=street_coords)

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        #In order to be able to receive payments, the account must be preset with these details
        #Use 000 000 0000 as the phone number and 000000 as the SMS code
        stripe_connect = stripe.Account.create(
            type="custom",
            country="GB",
            email= form.email.data,
            business_type="individual",
            individual={
                "email":form.email.data,
                "address" : {
                    "line1": form.address.data,
                    # "city": "London",
                    # "country": "GB",
                    # "postal_code": "SW1A 2AB"
                },
            },
            business_profile={
                "url": "https://theobaur.co.uk/",
            },
            capabilities={
                "transfers": {"requested": True},
            },
            tos_acceptance={
                "date": int(datetime.now().timestamp()),
                "ip": request.remote_addr,
            },
            company={
                "name": form.username.data,
            },
        )
        account_link = stripe.AccountLink.create(
            account=stripe_connect.id,
            refresh_url=url_for('register', _external=True), # This is where the user will be redirected to if they need to reauthenticate
            return_url=url_for("register_complete", _external=True), # This is where the user will be redirected to after they have authenticated
            type='account_onboarding',
        )
        onboarding_url = account_link.url

        session["user_data"] = {
            "username": form.username.data,
            "email": form.email.data,
            "password": form.password.data,
            "address": form.address.data,
            "remember": form.remember.data,
            "stripe_connect_id": stripe_connect.id
        }
        return redirect(onboarding_url)
    
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{error}", "danger")
    return render_template("register.html", title="Register", form=form)

#This is the page that the user will be redirected to after they have completed the onboarding process, mostly backend stuff
@app.route("/register/complete")
def register_complete():
    user_data = session.pop("user_data", None)
    if not user_data:
        flash("You must complete the onboarding process before accessing this page", "danger")
        return redirect(url_for("register"))
    customer = stripe.Customer.create(
        email=user_data["email"],
        name=user_data["username"]
    )
    user = User(username=user_data["username"], email=user_data["email"], password=user_data["password"], address=user_data["address"], stripe_customer_id=customer.id, stripe_connect_id=user_data["stripe_connect_id"], is_verified=False)
    db.session.add(user)
    db.session.commit()
    flash(f"Account created for {user_data['username']}!", "success")
    login_user(user, remember=user_data["remember"], duration=timedelta(days=7))
    token = s.dumps(user.email, salt="email-confirm")
    confirm_url = url_for("confirm_email", token=token, _external=True)
    email_content = render_template("email_accountcreation.html", confirm_url=confirm_url)
    mailer.send_html(user.email, email_content, "Registration")
    return redirect(url_for("home"))

@app.route("/confirm_email/<token>")
def confirm_email(token):
    try:
        email = s.loads(token, salt="email-confirm", max_age=172800)
    except SignatureExpired:
        flash("The token is expired!", "danger")
        return redirect(url_for("home"))
    user = User.query.filter_by(email=email).first()
    user.is_verified = True
    db.session.commit()
    flash(f"Email confirmed for {user.username}!", "success")
    return redirect(url_for("home"))

@app.route("/resend_email_confirmation")
@login_required
def resend_email_confirmation():
    token = s.dumps(current_user.email, salt="email-confirm")
    print (token)
    confirm_url = url_for("confirm_email", token=token, _external=True)
    email_content = render_template("email_accountcreation.html", confirm_url=confirm_url)
    mailer.send_html(current_user.email, email_content, "Registration")
    flash(f"Email confirmation resent to {current_user.email}!", "success")
    return redirect(url_for("home"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.hashed_password, form.password.data):
                login_user(user, remember=form.remember.data, duration=timedelta(days=7))
                flash(f"Logged in {form.username.data}!", "success")
                return redirect(url_for("home"))
        flash(f"Login unsuccessful. Please check username and password", "danger")
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash(f"Logged out", "success")
    return redirect(url_for("home"))

@app.route("/create_listing", methods=["GET", "POST"])
@login_required
def create_listing():
    if current_user.is_banned:
        flash(f"You have been banned from creating listings, please contact the moderators to review", "danger")
        return redirect(url_for("home"))
    elif not current_user.is_verified:
        flash(f"You must verify your email before creating a listing", "danger")
        return redirect(url_for("home"))
    form = CreateListingForm()

    ######OLD CODE FOR PAYMENT METHOD SAVING######
    # #If the user is redirected back to the create listing page from the payment page, add the payment method to the database
    # if request.args.get('session_id'):
    #     setup_intent_id = stripe.checkout.Session.retrieve(request.args.get('session_id')).setup_intent
    #     payment_method = stripe.SetupIntent.retrieve(setup_intent_id).payment_method
    #     new_payment_method = StripePaymentMethods(user_id=current_user.id, payment_method_id=payment_method)
    #     db.session.add(new_payment_method)
    #     db.session.commit()

    # #If the user has no payment methods saved, redirect them to the payment page
    # user = User.query.filter_by(id=current_user.id).first()
    # if len(user.cards_saved) == 0:
    #     session = stripe.checkout.Session.create(
    #     payment_method_types=['card'],
    #     mode='setup',
    #     customer=current_user.stripe_customer_id,
    #     success_url=url_for("create_listing", _external=True)+"?session_id={CHECKOUT_SESSION_ID}",
    #     cancel_url=url_for("home", _external=True),
    #     )
    #     return redirect(session.url, code=303)

    #Save the listing to the database and as a Stripe product
    if form.validate_on_submit():
        if current_user.is_active:

            if form.image_path.data:
                filename = secure_filename(form.image_path.data.filename)
                form.image_path.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                filename = "default.jpg"
            
            if request.form["description"] == "":
                description = "No description provided"

            new_deposit = int(float(request.form["deposit"])*100)

            stripe_product = stripe.Product.create(
                name=request.form["name"],
                description=form.description.data,
                active=True,
                default_price_data={"currency": "gbp", "unit_amount_decimal": new_deposit}
            )

            place_id = findAddress(current_user.address)[0]
            street_id = getStreetID(place_id)
            public_address = getAddressName(street_id)
            lat = findCoords(street_id)[0]
            lng = findCoords(street_id)[1]

            tool = Tool(name=request.form["name"], description=form.description.data, owner=current_user.id, borrower=None, address=current_user.address, deposit=new_deposit, is_available=True, high_risk=form.high_risk.data, rental_period=request.form["rental_period"], image_path=filename, category=request.form["category"], stripe_id=stripe_product.id, public_address=public_address, lat=lat, lng=lng)
            db.session.add(tool)
            db.session.commit()

            flash(f"Tool created!", "success")
            return redirect(url_for("home"))
        flash(f"Please log in", "danger")
        return redirect(url_for("login"))
    return render_template("create_listing.html", title="Create Listing", form=form)

@app.route("/profile/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    products = Tool.query.filter_by(owner=user.id).all()           
    reviews = Review.query.filter_by(reviewee=user.id).all()
    if current_user.is_authenticated:
        account_link = stripe.AccountLink.create(
            account=user.stripe_connect_id,
            refresh_url=url_for("profile", username=current_user.username, _external=True),
            return_url=url_for("profile", username=current_user.username, _external=True),
            type="account_update",
        )
        onboarding_url = account_link.url
    else:
        onboarding_url = None
    average = 0
    for review in reviews:
        average += review.rating
    if len(reviews) > 0:
        average = average / len(reviews)
    return render_template("profile.html", title="Profile", user=user, reviews=reviews, products=products, average=round(average,2), onboarding_url=onboarding_url)

@app.route("/change_address/<user>", methods=["GET", "POST"])
@login_required
def change_address(user):
    if current_user.is_banned:
        flash(f"You have been banned from changing your address, please contact the moderators to review", "danger")
        return redirect(url_for("home"))
    form = ChangeAddressForm()
    if form.validate_on_submit() and int(current_user.id) == int(user):
        user = User.query.filter_by(id=current_user.id).first()
        tools = Tool.query.filter_by(owner=current_user.id).all()

        place_id = findAddress(request.form["address"])[0]
        street_id = getStreetID(place_id)
        public_address = getAddressName(street_id)
        lat = findCoords(street_id)[0]
        lng = findCoords(street_id)[1]

        user.address = request.form["address"]

        for tool in tools:
            tool.address = request.form["address"]
            tool.public_address = public_address
            tool.lat = lat
            tool.lng = lng

        db.session.commit()
        flash(f"Address changed!", "success")
        return redirect(url_for("home"))
    return render_template("change_address.html", title="Change Address", form=form)

@app.route("/report/<username>", methods=["GET", "POST"])
@login_required
def report(username):
    if current_user.is_banned:
        flash(f"You have been banned from reporting users, please contact the moderators to review", "danger")
        return redirect(url_for("home"))
    form = ReportForm()
    user = User.query.filter_by(username=username).first_or_404()
    if form.validate_on_submit():
        if current_user.is_active:
            report = Report(reporter=current_user.id, reported=user.id, description=request.form["description"], handled=False)
            db.session.add(report)
            db.session.commit()
            flash(f"Report submitted!", "success")
            return redirect(url_for("home"))
        flash(f"Please log in", "danger")
        return redirect(url_for("login"))
    return render_template("report.html", title="Report", form=form, user=user)

@app.route("/view_reports", methods=["GET", "POST"])
@login_required
def view_reports():
    form = BanForm()
    return_deposit_form = ReturnDepositForm()
    if current_user.is_active:
        if current_user.is_admin:
            unhandled_reports = Report.query.filter_by(handled=False).order_by(Report.timestamp.desc()).all()
            handled_reports = Report.query.filter_by(handled=True).order_by(Report.timestamp.desc()).all()
            unhandled_disputes = Dispute.query.filter_by(handled=False).order_by(Dispute.timestamp.desc()).all()
            handled_disputes = Dispute.query.filter_by(handled=True).order_by(Dispute.timestamp.desc()).all()
            if form.validate_on_submit():
                report = Report.query.filter_by(id=request.form["reported"]).first_or_404()
                user = User.query.filter_by(id=report.reported).first_or_404()
                if request.form["action"] == "ban":
                    user.is_banned = True
                    report.handled = True
                    flash(f"{user.username} banned!", "success")
                elif request.form["action"] == "ignore":
                    user.is_banned = False
                    report.handled = True 
                    flash(f"{user.username} not banned!", "success")
                db.session.commit()
                return redirect(url_for("view_reports"))
            if return_deposit_form.validate_on_submit():
                dispute = Dispute.query.filter_by(id=request.form["disputed"]).first_or_404()   
                tool = Tool.query.filter_by(id=dispute.tool).first_or_404()
                admin = User.query.filter_by(username="admin").first_or_404()
                order = Order.query.filter_by(tool=dispute.tool, owner=dispute.owner, orderer=dispute.orderer, is_accepted=False).first_or_404()
                if request.form["action"] == "return_to_owner":
                    user = User.query.filter_by(id=tool.owner).first_or_404()
                    transfer = stripe.Transfer.create(
                        amount=str(int(tool.deposit)),
                        currency="gbp",
                        destination=user.stripe_connect_id,
                    )
                    tool.is_available = True
                    dispute.handled = True
                    order.is_accepted = True
                    #Send message to owner from admin saying that they won the dispute and will win the deposit
                    #Send message to borrower from admin saying that they lost the dispute and will lose the deposit
                    message1 = Message(sender=admin.id, receiver=user.id, message=f"Your dispute has been resolved and you have won the deposit for {tool.name}. A transfer of £{tool.deposit/100:.2f} has been made to your account.")
                    message2 = Message(sender=admin.id, receiver=tool.borrower, message=f"Your dispute has been resolved and you have lost the deposit for {tool.name}. A transfer of £{tool.deposit/100:.2f} has been made to the owner's account.")
                    db.session.add(message1)
                    db.session.add(message2)
                    db.session.commit()
                elif request.form["action"] == "return_to_borrower":
                    user = User.query.filter_by(id=tool.borrower).first_or_404()
                    transfer = stripe.Transfer.create(
                        amount=str(int(tool.deposit)),
                        currency="gbp",
                        destination=user.stripe_connect_id,
                    )
                    tool.is_available = True
                    dispute.handled = True
                    order.is_accepted = True
                    #Send message to owner from admin saying that they lost the dispute and will lose the deposit
                    #Send message to borrower from admin saying that they won the dispute and will win the deposit
                    message1 = Message(sender=admin.id, receiver=tool.owner, message=f"Your dispute has been resolved and you have lost the deposit for {tool.name}. A transfer of £{tool.deposit} has been made to the borrower's account.")
                    message2 = Message(sender=admin.id, receiver=user.id, message=f"Your dispute has been resolved and you have won the deposit for {tool.name}. A transfer of £{tool.deposit} has been made to your account.")
                    db.session.add(message1)
                    db.session.add(message2)
                    db.session.commit()
                elif request.form["action"] == "ignore":
                    dispute.handled = True
                    order.is_accepted = True
                    flash(f"Dispute ignored", "success")
                db.session.commit()
                return redirect(url_for("view_reports"))
            return render_template("view_reports.html", title="View Reports", unhandled_reports=unhandled_reports, handled_reports=handled_reports, form=form, return_deposit_form=return_deposit_form, unhandled_disputes=unhandled_disputes, handled_disputes=handled_disputes)
        flash(f"Please log in as admin", "danger")
        return redirect(url_for("login"))
    flash(f"Please log in", "danger")
    return redirect(url_for("login"))

@app.route("/show_cart", methods=["GET", "POST"])
@login_required
def show_cart():
    if current_user.is_banned:
        flash(f"You have been banned from purchasing, please contact the moderators to review", "danger")
        return redirect(url_for("home"))
    if current_user.is_verified == False:
        flash(f"You must verify your account before you can purchase", "danger")
        return redirect(url_for("home"))
    if current_user.is_active:
        if request.form.get("add_item"):
            tool = Tool.query.filter_by(id=request.form["add_item"]).first_or_404()
            if tool.is_available:
                cartItem = CartItem(user_id=current_user.id, tool_id=tool.id)
                tool.is_available = False
                db.session.add(cartItem)
                db.session.commit()
                flash(f"{tool.name} added to cart!", "success")
                return redirect(url_for("show_cart"))
            flash(f"{tool.name} is not available!", "danger")
            return redirect(url_for("show_cart"))

        if request.form.get("remove_item"):
            tool = Tool.query.filter_by(id=request.form["remove_item"]).first_or_404()
            cartItem = CartItem.query.filter_by(user_id=current_user.id, tool_id=tool.id).first_or_404()
            tool.is_available = True
            db.session.delete(cartItem)
            db.session.commit()
            flash(f"{tool.name} removed from cart!", "success")
            return redirect(url_for("show_cart"))

        cart = CartItem.query.filter_by(user_id=current_user.id).all()
        total = 0
        if cart:
            tools = Tool.query.join(CartItem, CartItem.tool_id == Tool.id).filter(CartItem.user_id == current_user.id).all()
            for tool in tools:
                total += tool.deposit
            return render_template("show_cart.html", title="Cart", tools=tools, total=total)
        else:
            return render_template("show_cart.html", title="Cart", tools=[])

    flash(f"Please log in", "danger")
    return redirect(url_for("login"))

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    if current_user.is_banned:
        flash(f"You have been banned from purchasing, please contact the moderators to review", "danger")
        return redirect(url_for("home"))
    if current_user.is_verified == False:
        flash(f"You must verify your account before you can purchase", "danger")
        return redirect(url_for("home"))
    form = CheckoutForm()
    if current_user.is_active:
        tools = Tool.query.join(CartItem, CartItem.tool_id == Tool.id).filter(CartItem.user_id == current_user.id).all() #Im not sure if I ever added something to expire carts - look into later
        total = 0
        tool_count = 0
        for tool in tools:
            total += tool.deposit
            tool_count += 1
        if form.validate_on_submit():   
            #Test card number: 4000 0000 0000 0077 
            #Test card expiry: 04/24
            #Test card CVC: 242

            line_items = []
            for tool in tools:
                product = stripe.Product.retrieve(tool.stripe_id)
                priceID = stripe.Price.list(product=product.id)["data"][0]["id"]
                line_items.append({
                    "price": priceID,
                    "quantity": 1
                })

            checkout_session = stripe.checkout.Session.create(
                mode = "payment",
                customer = current_user.stripe_customer_id,
                line_items = line_items,
                success_url = url_for("checkout_success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url = url_for("checkout", _external=True)
            )
            return redirect(checkout_session.url, code=303)
        return render_template("checkout.html", title="Checkout", tools=tools, total=total, form=form, tool_count=tool_count)
    flash(f"Please log in", "danger")
    return redirect(url_for("login"))

#This is a redirect page that will be called after the checkout is successful, only used for backend stuff
@app.route("/checkout_success", methods=["GET", "POST"])
@login_required
def checkout_success():
    if request.args.get("session_id"):
        session_id = request.args.get("session_id")
        session = stripe.checkout.Session.retrieve(session_id)
        if session["customer"] == current_user.stripe_customer_id and session["status"] == "complete":
            tools = Tool.query.join(CartItem, CartItem.tool_id == Tool.id).filter(CartItem.user_id == current_user.id).all() #Im not sure if I ever added something to expire carts - look into later
            for tool in tools:
                tool.borrower = current_user.id  
                tool.is_available = False
                order = Order(orderer=current_user.id, owner=tool.owner, tool=tool.id, rental_start=datetime.utcnow(), rental_end=datetime.utcnow() + timedelta(days=tool.rental_period))#######################
                message = Message(sender=current_user.id, receiver=tool.owner, message=f"{current_user.username} has borrowed your {tool.name} tool. Please contact them to arrange a time to pick it up.")
                db.session.add_all([order, message])
                db.session.delete(CartItem.query.filter_by(user_id=current_user.id, tool_id=tool.id).first_or_404())
                db.session.commit()
            flash(f"Checkout successful!", "success")
            return redirect(url_for("home"))
    flash(f"Checkout unsuccessful, please contact our team", "danger")
    return redirect(url_for("home"))

@app.route("/messages", methods=["GET", "POST"])    #TODO: In conversations tab, the latest message is the latest received, not the latest sent or received
@login_required
def messages():
    if current_user.is_banned:
        flash(f"You have been banned from messaging, please contact the moderators to review", "danger")
        return redirect(url_for("home"))
    if current_user.is_active:
        recent_messages = Message.query.filter_by(receiver=current_user.id).order_by(Message.timestamp.desc()).group_by(Message.sender).all()
        pending_messages = Message.query.filter(and_(Message.sender == current_user.id, ~Message.receiver.in_([m.sender for m in recent_messages]))).order_by(Message.timestamp.desc()).group_by(Message.receiver).all()
        return render_template("messages.html", title="Messages", recent_messages=recent_messages, pending_messages=pending_messages)
    return redirect(url_for("login"))

@app.route("/chat/<chat_id>", methods=["GET", "POST"])
@login_required
def chat(chat_id): #s(sender_ID)r(receiver_ID)
    if current_user.is_banned:
        flash(f"You have been banned from messaging, please contact the moderators to review", "danger")
        return redirect(url_for("home"))
    form = MessageForm()
    validator = re.compile(r"^s\d+r\d+$")
    match = validator.search(chat_id)
    if match:
        sender_id = chat_id.split("r")[0][1:]
        receiver_id = chat_id.split("r")[1]
        sender = User.query.filter_by(id=sender_id).first_or_404()
        receiver = User.query.filter_by(id=receiver_id).first_or_404()
        if current_user.is_active:
            if current_user.id == int(receiver_id):
                messages = Message.query.filter((Message.sender.in_([sender_id, receiver_id])) & (Message.receiver.in_([sender_id, receiver_id]))).order_by(Message.timestamp.asc()).all()
                if form.validate_on_submit():
                    message = Message(sender=current_user.id, receiver=sender_id, message = form.message.data)
                    email=sender.email
                    email_content = render_template("email_newmessage.html", message=form.message.data, sender=sender_id, receiver=receiver_id)
                    mailer.send_html(email, email_content, "Registration")
                    db.session.add(message)
                    db.session.commit()
                    return redirect(url_for("chat", chat_id=chat_id))
                return render_template("chat.html", title="Chat", messages=messages, sender=sender, receiver=receiver, form=form)
            flash(f"Please log in", "danger")
            return redirect(url_for("login"))
    else:
        #return redirect(url_for("error_404"))
        abort(404)
    return render_template("chat.html", title="Chat")

@app.route("/listings", methods=["GET", "POST"])
@login_required
def listings():
    if current_user.is_banned:
        flash(f"You have been banned from listing tools, please contact the moderators to review", "danger")
        return redirect(url_for("home"))
    #If lender has not comfirmed the return of the tool before rental period is up then a dispute is opened
    form = ConfirmForm()
    removeListingForm = RemoveListingForm()
    if current_user.is_active:
        tools = Tool.query.filter_by(owner=current_user.id).all()
        orders = Order.query.filter_by(owner=current_user.id).all()
        if request.form.get("confirm_return"):
            order = Order.query.filter_by(id=request.form.get("confirm_return")).first_or_404()
            order.is_accepted = True
            tool = Tool.query.filter_by(id=order.tool).first_or_404()
            tool.is_available = True
            flash(f"Tool returned, transferring depoit back to borrower", "success")
            #Return deposit to borrower using Stripe
            #https://stripe.com/docs/api/transfers/create?lang=python
            transfer = stripe.Transfer.create(
                currency="gbp",
                destination=tool.tools_borrowed.stripe_connect_id,
                amount=str(int(tool.deposit)),
            )
            tool.borrower = None
            db.session.commit()
            return redirect(url_for("listings"))
        
        for order in orders:
            if datetime.utcnow() > order.rental_end and not order.is_accepted:
                #An admin must open communication with the buyer and seller to resolve the issue and return the deposit to whichever party is in the right, if either party does not respond within a certain time period then they lose the dispute and the deposit is returned to the other party
                flash(f"{order.orders_made.name} has not been returned withing the rental period, please report the user and file a dispute", "success")
            
        if request.form.get("remove_listing"):
            tool = Tool.query.filter_by(id=request.form.get("remove_listing")).first_or_404()
            db.session.delete(tool)
            db.session.commit()
            flash(f"Tool removed from listings", "success")
            return redirect(url_for("listings"))
        return render_template("listings.html", title="Listings", orders=orders, form=form, tools=tools, removeListingForm=removeListingForm)
    return redirect(url_for("login"))

@app.route("/dispute/<order_id>", methods=["GET", "POST"])
@login_required
def dispute(order_id):
    if current_user.is_banned:
        flash(f"You have been banned from filing disputes, please contact the moderators to review", "danger")
        return redirect(url_for("home"))
    form = DisputeForm()
    order = Order.query.filter_by(id=order_id).first_or_404()
    if form.validate_on_submit():
        admin = User.query.filter_by(username="admin").first_or_404()
        if current_user.id == order.orderer:
            dispute = Dispute(orderer=current_user.id, owner=order.owner, tool=order.tool, description=form.description.data)
            message1 = Message(sender=admin.id, receiver=order.owner, message = f"Dispute opened against you for {order.orders_made.name}")
            message2 = Message(sender=admin.id, receiver=order.orderer, message = f"Dispute opened successfully for {order.orders_made.name}")
            db.session.add(message1)
            db.session.add(message2)
            db.session.commit()
        elif current_user.id == order.owner:
            if datetime.utcnow() > order.rental_end:
                dispute = Dispute(orderer=order.orderer, owner=current_user.id, tool=order.tool, description=form.description.data)
                message1 = Message(sender=admin.id, receiver=order.owner, message = f"Dispute opened successfully for {order.orders_made.name}")
                message2 = Message(sender=admin.id, receiver=order.orderer, message = f"Dispute opened against you for {order.orders_made.name}")
                db.session.add(message1)
                db.session.add(message2)
                db.session.commit()
            else:
                flash(f"Dispute can only be opened after rental period has ended", "danger")
                return redirect(url_for("home"))
        db.session.add(dispute)
        db.session.commit()
        flash(f"Dispute opened", "success")
        return redirect(url_for("home"))
    return render_template("dispute.html", title="Dispute", form=form, order=order)

@app.route("/orders")
@login_required
def orders():
    if current_user.is_active:
        active_orders = Order.query.filter_by(orderer=current_user.id, is_accepted=False).all()
        completed_orders = Order.query.filter_by(orderer=current_user.id, is_accepted=True).all()
        return render_template("orders.html", title="Orders", active_orders=active_orders, completed_orders=completed_orders)
    return redirect(url_for("login"))

@app.route("/review/<order_id>", methods=["GET", "POST"])
@login_required
def review(order_id):
    order = Order.query.filter_by(id=order_id).first_or_404()
    if current_user.id == order.orderer:
        print (order.reviews)
        if order.is_accepted:
            if order.reviews == []:
                form = ReviewForm()
                if form.validate_on_submit():
                    review = Review(order=order.id, reviewer=current_user.id, reviewee=order.owner, tool_id=order.tool, rating=form.rating.data, comments=form.description.data)
                    db.session.add(review)
                    db.session.commit()
                    flash(f"Review submitted", "success")
                    return redirect(url_for("home"))
                return render_template("review.html", title="Review", form=form)
            else:
                flash(f"Review already submitted", "danger")
                return redirect(url_for("home"))
        else:
            flash(f"Review can only be submitted after the order has been finalized", "danger")
            return redirect(url_for("home"))
    else:
        flash(f"Review can only be submitted by the orderer", "danger")
        return redirect(url_for("home"))

@app.route("/edit_listing/<tool_id>", methods=["GET", "POST"])
@login_required
def edit_listing(tool_id):
    if current_user.is_banned:
        flash(f"You have been banned from editing listings, please contact the moderators to review", "danger")
        return redirect(url_for("home"))
    tool = Tool.query.filter_by(id=tool_id).first_or_404()
    form = EditListingForm(high_risk=tool.high_risk)
    if current_user.is_active and current_user.id == tool.owner:
        if tool.is_available:
            form.name.data = tool.name
            form.description.data = tool.description
            form.deposit.data = tool.deposit/100
            form.rental_period.data = tool.rental_period
            form.category.data = tool.category
            if form.validate_on_submit():
                if form.image_path.data:
                    filename = secure_filename(form.image_path.data.filename)
                    form.image_path.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    tool.image_path = filename
                else:
                    filename = "default.jpg"
                tool.name = request.form["name"]
                tool.description = request.form["description"]
                new_deposit = int(float(request.form["deposit"])*100)
                if int(tool.deposit) != new_deposit:
                    newprice = stripe.Price.create(currency="gbp", unit_amount=new_deposit, product=tool.stripe_id)
                    stripe.Product.modify(tool.stripe_id, default_price=newprice.id)
                tool.deposit = new_deposit
                tool.rental_period = request.form["rental_period"] 
                tool.high_risk = form.high_risk.data    
                tool.category = request.form["category"]
                db.session.commit()
                stripe.Product.modify(tool.stripe_id, name=tool.name, description=tool.description)
                flash(f"Tool details updated!", "success")
                return redirect(url_for("listings"))
            return render_template("edit_listing.html", title="Edit Listing", form=form)
        flash(f"Tool is currently being rented, please wait until the rental period is over to edit the listing", "danger")
        return redirect(url_for("listings"))
    return redirect(url_for("login"))

@app.route("/map_view")
@login_required
def map_view():
    address = current_user.address
    #Get place_id of the user's address for distance matrix
    center_points_list = findAddress(address)
    if center_points_list == None:
        flash(f"Address associated with your account is invalid", "danger")
        return redirect(url_for("home"))
    else:
        center_place_id = center_points_list[0]


    #Get the address of the user as a coordinates
    center_point = findCoords(center_place_id)

    #Get the place_id of the street of all the tools within 2 miles of the user
    tools = Tool.query.filter_by(is_available=True).all()
    tool_location_data = {}
    for tool in tools:
        #if 10 > float(distance(tool.address, center_place_id)[0].split(" ")[0].replace(',', '')):
            tool_location_data[tool.name] = {
                "coords": [tool.lat, tool.lng],
                "id": tool.id,
                "deposit": tool.deposit,
                "owner": tool.tools_listed.username,
                "category": tool.category,
                "high_risk": tool.high_risk,
                "rental_period": tool.rental_period,
            }
    #print (tool_location_data)
    return render_template("map_view.html", title="Map View", center_point=center_point, tool_location_data=tool_location_data)
    
@app.route("/success")
@login_required
def success():
    return render_template("success.html", title="Success")

@app.route("/cancel", methods=["POST"])
@login_required
def cancel():
    return render_template("cancel.html", title="Cancel")

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/termsconditions")
def termsconditions():
    return render_template('TermsConditions.html', title='Terms & Conditions')

#@app.errorhandler(404)
#def error_404(error):
#    return "404 Page not Found", 404


## sorting fuction
def sortResults(theData, current_search, current_searchloc, search_radius):
    deleteTools = []

    if theData == "pdesc":
        theTools = Tool.query.order_by(Tool.deposit.desc()).filter(Tool.name.contains(current_search)).all()
    elif theData == "pasc":
        theTools = Tool.query.order_by(Tool.deposit.asc()).filter(Tool.name.contains(current_search)).all()
    elif theData == "rdesc":
        theTools = Tool.query.order_by(Tool.rental_period.desc()).filter(Tool.name.contains(current_search)).all()
    elif theData == "rasc":
        theTools = Tool.query.order_by(Tool.rental_period.asc()).filter(Tool.name.contains(current_search)).all()
    elif theData == "ridesc":
        theTools = Tool.query.order_by(Tool.high_risk.desc()).filter(Tool.name.contains(current_search)).all()
    elif theData == "riasc":
        theTools = Tool.query.order_by(Tool.high_risk.asc()).filter(Tool.name.contains(current_search)).all()
    else:
        theTools = Tool.query.filter(Tool.name.contains(current_search)).all()

    if current_searchloc != "":
        for tool in theTools:
            if float(search_radius) < float(distance(tool.address, current_searchloc)[0].split(" ")[0].replace(',', '')):
                deleteTools.append(tool)

    theTools = [tool for tool in theTools if tool not in deleteTools]

    return theTools            
