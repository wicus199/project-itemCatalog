# Import flask package
# TODO: Line length
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
# Import a new session as login_session to create unique session token
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
# Used to import client_id and client_secret from json file
from oauth2client.client import flow_from_clientsecrets  
# Catches error if authorization code to token exchange fails
from oauth2client.client import FlowExchangeError        
from database import Base, Category, Item, User
# Random and string used to generate pseudo random string to identify sessions
import random
import string
#Http client library
import httplib2     
import json
#from flask import make_response     # Converts return value from a function into a response object to send to client
import requests     # Apache http library


app = Flask(__name__)
# Read client id from client_secrets.json file
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogDatabaseWithUsers')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
# this token will be stored in a session to validate later on
@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Is correct STATE token received from client
    if request.args.get('state') != login_session['state']:
        # 401 Unauthorized: Authentication is required but failed
        response = make_response(json.dumps('Incorrect state token received.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain the authorization code if states match
    # Obtain code from request data
    code = request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # Exchange authorization code for credentials using step2_exchange
        # Creates a Oauth2Credentials object
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Authorization code exchange failed'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Return the access token and its expiration information.
    # Store it in access_token
    access_token = credentials.access_token
    print(access_token)
    # Url provided by google to check if access token is valid
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={0}'.format(access_token))

    r = requests.get(url)
    result = json.loads(r.text)

    # If there was an error:
    if result.get('error') is not None:
        # We don't know what the error is yet, thus return code 500
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        print(response)     # For debugging
        return response

    # If this point is reached, the access token is valid.
    # Now we have to determine if it is used for the intended user.

    gplus_id = credentials.id_token['sub']  # TODO: id_token?
    # If user_id's do not match
    print("User_id: {0}".format(result['user_id']))
    print("gplus_id: {0}".format(gplus_id))
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps('User IDs do not match'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # If this point is reached, access token is valid for specific user
    # Determine if access token is valid for this specific location
    # TODO: check values of result from google docs
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client_id and app id does not match"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    user_access_token = login_session.get('access_token')
    user_gplus_id = login_session.get('gplus_id')
    if user_access_token is not None and gplus_id == user_gplus_id:
        response = make_response(json.dumps('User already logged in.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store access token
    login_session['access_token'] = credentials.access_token
    print(login_session['access_token'])
    login_session['gplus_id'] = gplus_id

    # Get user info from provider
    # Url from google docs
    url_info = "https://www.googleapis.com/oauth2/v1/userinfo"
    q_params = {'access_token':credentials.access_token, 'alt':'json'}
    user_info = requests.get(url_info, params = q_params)

    # Do json decoding on user_info
    user_data = user_info.json()

    login_session['username'] = user_data['name']
    login_session['picture'] = user_data['picture']
    login_session['email'] = user_data['email']

    # Create a new user if the user does not exist
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # This needs to be passed to the template in another way. This is dirty
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    #flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output

# Disconnect user
@app.route("/gdisconnect")
def gdisconnect():
    access_token = login_session['access_token']
    print(access_token)
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke'
    params = {'token':access_token}
    result = requests.get(url, params=params)
    print(result.url)
    print(result.status_code)

    if result.status_code == 200:
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("You were successfully logged out!")
        return redirect('/catalog')
        #return response
    else:
        # 400: Bad request
        response = make_response(json.dumps('Failed to revoke client token.'), 400)
        response.headers['Content-Type'] = 'application.json'
        return response


# Main catalog page -- Methods: GET
@app.route('/')
@app.route('/catalog/')
def catalog():
    # Query all categories to display main_catalog
    main_catalog = session.query(Category).all()
    admin = False
    # If user is not admin user, don't render add category button
    if 'username' in login_session:
        if login_session['email'] == 'wicus92@gmail.com':
            admin = True
    # Pass main_catalog to catalog.html page (main page) into catalog_items
    return render_template('catalog.html', catalog_items=main_catalog, login=login_session, admin=admin)

@app.route('/catalog/json')
def catalogJson():
    categories = session.query(Category).all()
    return jsonify(Categories=[category.serialize for category in categories])


# View the contents of a category -- Methods: GET
@app.route('/catalog/<int:category_id>/')
def viewCategory(category_id):
    admin = False
    # If user is not admin, don't render edit and delete category buttons in html
    if 'username' in login_session:
        if login_session['email'] == 'wicus92@gmail.com':
            admin = True
    
    # Query the items in a category
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return render_template('category.html', category=category, itemList=items, login=login_session, admin=admin)
    
# JSON endpoint containing info of a single category
@app.route('/catalog/<int:category_id>/json')
def viewCategoryJson(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    return jsonify(Category=[category.serialize])
    
# JSON endpoint containing items in a category
@app.route('/catalog/<int:category_id>/items/json')
def viewItemsJson(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(CategoryItems=[item.serialize for item in items])
    
# Add a category -- Methods: GET, POST
@app.route('/catalog/add/', methods=['GET','POST'])
def addCategory():
    # Only the admin account of the website is allowed to add a category
    # The if statement prevents a user to get direct access through url
    if 'username' not in login_session:
        return redirect('/login')
    if login_session['email'] != 'wicus92@gmail.com':
        # Access denied. Render access denied page
        return render_template('accessDenied.html')
    admin = True
    # Default image for category located in static folder
    default_img = '/static/category_default.jpg'

    if request.method == 'POST':
        if not(request.form['pic_url']):
            url = default_img
        else:
            url = request.form['pic_url']
        newCat = Category(
            name=request.form['itemName'],
            description=request.form['description'],
            url=url,
            user_id=login_session['user_id'])
        session.add(newCat)
        session.commit()
        return redirect(url_for('catalog'))
    else:
        return render_template('addCategory.html', login=login_session, admin=admin)

# Edit a category -- Methods: GET, POST
@app.route('/catalog/<int:category_id>/edit/', methods=['GET','POST'])
def editCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    # Only the admin account of the website is allowed to edit a category
    # The if statement prevents a user to get direct access through url
    if 'username' not in login_session:
        return redirect('/login')
    if login_session['email'] != 'wicus92@gmail.com':
        # Access denied. Render access denied page
        return render_template('accessDenied.html')
    admin = True
    default_img = '/static/category_default.jpg'
    if request.method == 'POST':
        if not(request.form['pic_url']):
            url = default_img
        else:
            url = request.form['pic_url']
        category.name = request.form['itemName']
        category.description = request.form['description']
        category.url = url
        session.add(category)
        session.commit()
        return redirect(url_for('viewCategory', category_id=category.id))
    else:
        return render_template('editCategory.html', category=category, login=login_session, admin=admin)

# Delete a category -- Methods: GET, POST
@app.route('/catalog/<int:category_id>/delete/', methods=['GET','POST'])
def deleteCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    # Only the admin account of the website is allowed to delete a category
    # The if statement prevents a user to get direct access through url
    if 'username' not in login_session:
        return redirect('/login')
    if login_session['email'] != 'wicus92@gmail.com':
        # Access denied. Render access denied page
        return render_template('accessDenied.html')
    admin = True
    if request.method == 'POST':
        session.delete(category)
        session.commit()
        return redirect(url_for('catalog'))
    else:
        return render_template('deleteCategory.html', category=category, login=login_session, admin=admin)

# View an item -- Methods: GET
@app.route('/catalog/<int:category_id>/item/<int:item_id>/')
def viewItem(category_id, item_id):
    # Add parameter to render_template to render buttons based on whether user is logged in
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    itemOwnerID = item.user_id
    # If a user is logged in and owner of item, buttons will render to edit and delete item. 
    # Otherwise no buttons, but a message.
    if 'username' in login_session and (itemOwnerID == login_session['user_id'] or login_session['email'] == 'wicus92@gmail.com'):
        userAccess = True
    else:
        userAccess = False
    return render_template('items.html', category=category, item=item, login=login_session, userAccess=userAccess)

# JSON endpoint to view information on a single item
@app.route('/catalog/<int:category_id>/item/<int:item_id>/json')
def viewItemJson(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)

# Create a new item inside a category -- Methods: GET, POST
@app.route('/catalog/<int:category_id>/add/', methods=['GET','POST'])
def addItem(category_id):
    # This if statement prevents the user from accessing directly from link
    if 'username' not in login_session:
        return redirect('/login')

    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    cat_id = request.form.get('cat-name')

    itemCreator = getUserId(login_session['email'])
    default_img = '/static/random_item.jpg'

    if request.method == 'POST':
        if not(request.form['pic_url']):
            url = default_img
        else:
            url = request.form['pic_url']
        newItem = Item(
            name = request.form['itemName'],
            description = request.form['description'],
            url = url,
            category_id = int(cat_id),
            user_id = itemCreator
        )
        session.add(newItem)
        session.commit()
        #returns to the page of the selected category of the new item
        return redirect(url_for('viewCategory', category_id=int(cat_id)))
    else:
        return render_template('addItem.html', category=category, categories=categories, login=login_session)

# Edit an item -- Methods: GET, POST
@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit/', methods=['GET','POST'])
def editItem(category_id, item_id):
    # Query first to get user_id of item
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    creatorID = item.user_id
    
    # Do these the same as category. Don't render buttons in viewItem when user is not creator.
    # Also need to prevent user from accessing link directly
    if 'username' not in login_session:
        return redirect('/login')
    # Unauthorized user tried to access directly from url
    userId = getUserId(login_session['email'])
    if login_session['email'] != 'wicus92@gmail.com':
        if userId != creatorID:
            return render_template('accessDenied.html')
        
    categories = session.query(Category).all()
    cat_id = request.form.get('cat-name')
    default_img = '/static/random_item.jpg'

    if request.method == 'POST':
        if not(request.form['pic_url']):
            url = default_img
        else:
            url = request.form['pic_url']
        item.name = request.form['itemName']
        item.description = request.form['description']
        item.url = url
        item.category_id = request.form.get('cat-name')    #request.form.get('')
        session.add(item)
        session.commit()
        return redirect(url_for('viewItem', category_id=cat_id, item_id=item.id))
    else:
        return render_template('editItem.html', categories=categories, category=category, item=item, login=login_session)

# Delete an item -- Methods: GET, POST
@app.route('/catalog/<int:category_id>/item/<int:item_id>/delete/', methods=['GET','POST'])
def deleteItem(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    creatorID = item.user_id
    
    if 'username' not in login_session:
        return redirect('/login')
    # Unauthorized user tried to access directly from url
    userId = getUserId(login_session['email'])
    if login_session['email'] != 'wicus92@gmail.com':
        if userId != creatorID:
            return render_template('accessDenied.html')

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('viewCategory', category_id=category.id))
    else:
        return render_template('deleteItem.html', category=category, item=item, login=login_session,)

# Function that takes in a user id and returns a User object containing user info
def getUserInfo(user_id):
    user_info = session.query(User).filter_by(user_id=user_id)
    return user_info

# Function that takes a user email as parameter and returns the user id if the user exists
# user id needed to get user info
def getUserId(user_email):
    try:
        user = session.query(User).filter_by(email=user_email).one()
        return user.id
    except:
        return None

# Creates a user by using credentials stored in login_session from gconnect
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    # Retrieve user id that can be used when requesting user info
    user = session.query(User).filter_by(email=login_session['email']).one()
    user_id = user.id
    return user_id


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)