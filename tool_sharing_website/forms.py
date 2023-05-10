from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, RadioField, SelectField, DecimalField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, email_validator, Optional, NumberRange
from tool_sharing_website.models import User
from tool_sharing_website.routes import flash
from datetime import timedelta
from tool_sharing_website.maps import findAddress, getStreetID
from decimal import Decimal


class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo("password",message="Passwords must match")])
    email = StringField('Email', validators=[DataRequired(), Email(check_deliverability=True)])
    address = StringField('Address', validators=[DataRequired()]) 
    remember = BooleanField('Remember Me')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            #flash(f"Username already exists", "danger")
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            #flash(f"Email already exists", "danger")
            raise ValidationError('That email is taken. Please choose a different one.')

    def validate_password(self, password):
        errors = []
        if password.data.islower():
            #flash(f"Password must contain at least one uppercase letter", "danger")
            # raise ValidationError('Password must contain at least one uppercase letter')
            errors.append('Password must contain at least one uppercase letter')
        if password.data.isupper():
            #flash(f"Password must contain at least one lowercase letter", "danger")
            # raise ValidationError('Password must contain at least one lowercase letter')
            errors.append('Password must contain at least one lowercase letter')
        if password.data.isnumeric():
            #flash(f"Password must contain at least one letter", "danger")
            # raise ValidationError('Password must contain at least one letter')
            errors.append('Password must contain at least one letter')
        if password.data.isalpha():
            #flash(f"Password must contain at least one number", "danger")
            # raise ValidationError('Password must contain at least one number')
            errors.append('Password must contain at least one number')
        if errors:
            raise ValidationError(", ".join(errors))
        
    def validate_address(self, address):
        if findAddress(address.data)[0] == "":
            #flash(f"Address not found, try entering more information", "danger")
            raise ValidationError('Address not found, try entering more information')
        elif getStreetID(findAddress(address.data)[0]) == None:
            #flash(f"Postcode for this address cannot be found, try entering more information", "danger")
            raise ValidationError('Postcode for this address cannot be found, try entering more information')
        

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class DepositField(DecimalField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = int(Decimal(valuelist[0]) * 100)
            except (ValueError, TypeError):
                self.data = None
                raise ValueError(self.gettext('Invalid deposit value'))

class CreateListingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    deposit = DepositField('Deposit: £', validators=[DataRequired(), NumberRange(min=0.01, max=3000)])
    rental_period = IntegerField('Rental Period (days)', validators=[DataRequired(), NumberRange(min=1, max=90)])
    high_risk = BooleanField('High Risk')
    category = SelectField('Category', choices=[('garden', 'Garden'), ('kitchen', 'Kitchen'), ('home', 'Home'), ('other', 'Other')])
    image_path = FileField('Image')
    submit = SubmitField('Create Listing')

class ReportForm(FlaskForm):
    description = TextAreaField('Reason', validators=[DataRequired()])
    submit = SubmitField('Report')

class BanForm(FlaskForm):
    action = SelectField('Action', choices=[('ban', 'Ban'), ('ignore', 'Ignore')])
    submit = SubmitField('Handle')

class RemoveListingForm(FlaskForm):
    submit = SubmitField('Remove Listing')

class CheckoutForm(FlaskForm):
    submit = SubmitField('Checkout using Stripe')

class MessageForm(FlaskForm):
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

class SearchForm(FlaskForm):
    searchterm = StringField('Search Term')
    searchterm2 = StringField('Location', validators=[Length(min=4)])
    submit = SubmitField('Search')          
    
class FilterForm(FlaskForm):
    select2 = SelectField('Sort by:', choices=[('none1', 'None'),('pdesc', 'Price (Descending)'), ('pasc', 'Price (Ascending)'), ('rdesc', 'Rental Period (Descending)'), ('rasc', 'Rental Period (Ascending)'), ('ridesc', 'High risk first'), ('riasc', 'Low risk first')], render_kw={"onchange": "this.form.submit()"})
    #submit2 = SubmitField('Apply')

class DistForm(FlaskForm):
    select3 = SelectField('Within Distance:', choices=[('unlimited', 'Unlimited'), ('0.5', '0.5 Miles'), ('1', '1 Mile'), ('2', '2 Miles'), ('3', '3 Miles'), ('5', '5 Miles'), ('10', '10 Miles'), ('20', '20 Miles'), ('50', '50 Miles'), ('100', '100 Miles')], render_kw={"onchange": "this.form.submit()"})
    #submit3 = SubmitField('Apply')

class ConfirmForm(FlaskForm):
    submit = SubmitField('Confirm return')

class EditListingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    deposit = DepositField('Deposit: £', validators=[DataRequired(), NumberRange(min=0, max=3000)])
    rental_period = IntegerField('Rental Period (days)', validators=[DataRequired(), NumberRange(min=1, max=90)])
    high_risk = BooleanField('High Risk')
    category = SelectField('Category', choices=[('garden', 'Garden'), ('kitchen', 'Kitchen'), ('home', 'Home'), ('other', 'Other')])
    image_path = FileField()
    submit = SubmitField('Edit Listing')

class DisputeForm(FlaskForm):
    description = TextAreaField('Reason', validators=[DataRequired()])
    submit = SubmitField('Dispute')

class ReturnDepositForm(FlaskForm):
    action = SelectField('Action', choices=[('return_to_borrower', 'Return deposit to Borrower'), ('return_to_owner', 'Return deposit to Owner'), ('ignore', 'Ignore')])
    submit = SubmitField('Return Deposit')

class ChangeAddressForm(FlaskForm):
    address = StringField('Address', validators=[DataRequired()]) 
    submit = SubmitField('Change Address')

    def validate_address(self, address):
        if findAddress(address.data) == []:
            #flash(f"Address not found, try entering more information", "danger")
            raise ValidationError('Address not found, try entering more information')
        elif getStreetID(findAddress(address.data)[0]) == None:
            #flash(f"Postcode for this address cannot be found, try entering more information", "danger")
            raise ValidationError('Postcode for this address cannot be found, try entering more information')
        
class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    description = TextAreaField('Description')
    submit = SubmitField('Submit')