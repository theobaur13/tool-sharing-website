# Tool Sharing Website

A Flask-based website designed to let users borrow tools from one another. This website uses Stripe to manage deposit payments and returns. Google Maps API tools are used to display an interactive map, calculate the distances for location searching, as well as geocoding location data. SQLite is used to manage the database. The website enables users to create an account, search for tools based on keywords or location, borrow tools by paying a deposit which is returned when the tool is returned, message other users using a simple chat system and report and open disputes with other users.

## Installation

Clone repository

```bash
git clone https://github.com/theobaur13/tool-sharing-website
```
Set up virtual environment

```python
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
py wsgi.py
```
Create a file named **keys.py** into the **tool-sharing-website** directory and add API keys from [Stripe API](https://stripe.com/docs/api), [Google Maps API](https://developers.google.com/maps), your own custom generated Flask secret key, and your company email
```python
api_key = "GOOGLE_MAPS_API_KEY"
stripe_api_key = "STRIPE_PRIVATE_KEY"
stripe_public_key = "STRIPE_PUBLIC_KEY"
config_secret_key = "CUSTOM_CONFIG_KEY"
email_host = "EMAIL_HOST"
email_port = 000
email_user = "EMAIL@EMAIL.COM"
email_password = "EMAIL_PASSWORD"
```

## Usage

```python
venv\Scripts\activate

# launches website to localhost
py wsgi.py

#resets the database with the values in db_maker.py
py db_maker.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)