from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, SportCategory, SportingItem

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Sports Category App"

engine = create_engine('sqlite:///sportscatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)
    # return "The current session state is %s" % login_session['state']

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session.get('credentials')
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        print 'gdisconnect executed'
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        print 'gdisconnect did not execute'
        return response


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    print 'gdisconnect executed'
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            print 'gdisconnect executed'
            gdisconnect()

        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showSportCategory'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showSportCategory'))


# helper functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.userId


def getUserInfo(user_id):
    user = session.query(User).filter_by(userId=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.userId
    except:
        return None


# Show all Sports
@app.route('/')
@app.route('/category/')
def showSportCategory():
    sportcategory = session.query(SportCategory).order_by(asc(SportCategory.name))
    if 'username' not in login_session:
        return render_template('publicsportscategory.html', sportcategory=sportcategory)
    else:
        # return "This page will show all SportsCategory"
        return render_template('sportscategory.html', sportcategory=sportcategory)


# Create a new category
@app.route('/category/new/', methods=['GET', 'POST'])
def newSportCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        print login_session['user_id']
        newSportCategory = SportCategory(
            name=request.form['name'], userId=login_session['user_id'])
        session.add(newSportCategory)
        session.commit()
        flash(" Sport Category created.")
        return redirect(url_for('showSportCategory'))
    else:
        return render_template('newsportscategory.html')


# Edit a sport category
@app.route('/category/<int:sportCategory_id>/edit/', methods=['GET', 'POST'])
def editSportCategory(sportCategory_id):
    editedSportCategory = session.query(
        SportCategory).filter_by(id=sportCategory_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    print editedSportCategory.userId
    print login_session['user_id']
    if editedSportCategory.userId != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this Sport Category. Please create your own cat in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedSportCategory.name = request.form['name']
            return redirect(url_for('showSportCategory'))
    else:
        return render_template(
            'editSportCategory.html', sportcategory=editedSportCategory)


# Delete a sportCategory
@app.route('/category/<int:sportCategory_id>/delete/', methods=['GET', 'POST'])
def deleteSportCategory(sportCategory_id):
    sportCategoryToDelete = session.query(
        SportCategory).filter_by(id=sportCategory_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if sportCategoryToDelete.userId != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this Sport Category. Please create your own cat in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(sportCategoryToDelete)
        session.commit()
        return redirect(
            url_for('showSportCategory', sportCategory_id=sportCategory_id))
    else:
        return render_template(
            'deleteSportCategory.html', sportcategory=sportCategoryToDelete)
    # return 'This page will be for deleting sportCategory'


# Show sporting item
@app.route('/category/<int:sportCategory_id>/')
@app.route('/category/<int:sportCategory_id>/menu/')
def showMenu(sportCategory_id):
    sportcategory = session.query(SportCategory).filter_by(id=sportCategory_id).one()
    creator = getUserInfo(sportcategory.userId)
    items = session.query(SportingItem).filter_by(
        sport_cat_id=sportCategory_id).all()
    if 'username' not in login_session or creator.userId != login_session['user_id']:
        return render_template('publicmenuitem.html', items=items, sportcategory=sportcategory, creator=creator)
    else:
        return render_template('menuItem.html', items=items, sportcategory=sportcategory, creator=creator)


# Create a new sporting item
@app.route('/category/<int:sportCategory_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(sportCategory_id):
    if 'username' not in login_session:
        return redirect('/login')
    sportcategory = session.query(SportCategory).filter_by(id=sportCategory_id).one()
    if login_session['user_id'] != sportcategory.userId:
        return "<script>function myFunction() {alert('You are not authorized to add menu items to this restaurant. Please create your own restaurant in order to add items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        print request.form['name']
        print request.form['description']
        print sportCategory_id
        print sportcategory.userId
        newItem = SportingItem(name=request.form['name'], sport_cat_id=sportCategory_id, userId=sportcategory.userId,
                               description=request.form['description'])
        session.add(newItem)
        session.commit()
        flash("Item created.")
        return redirect(url_for('showMenu', sportCategory_id=sportCategory_id))
    else:
        return render_template('newmenuitem.html', sportCategory_id=sportCategory_id)


# edit a sporting item
@app.route('/category/<int:sportCategory_id>/menu/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editMenuItem(sportCategory_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(SportingItem).filter_by(id=menu_id).one()
    if login_session['user_id'] != editedItem.userId:
        return "<script>function myFunction() {alert('You are not authorized to edit menu items to this restaurant. Please create your own restaurant in order to edit items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash("Item Edited.")
        return redirect(url_for('showMenu', sportCategory_id=sportCategory_id))
    else:

        return render_template(
            'editSportItem.html', sportCategory_id=sportCategory_id, menu_id=menu_id, item=editedItem)


# Delete a sporting item
@app.route('/category/<int:sportCategory_id>/menu/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def deleteMenuItem(sportCategory_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(SportingItem).filter_by(id=menu_id).one()
    if login_session['user_id'] != itemToDelete.userId:
        return "<script>function myFunction() {alert('You are not authorized to delete menu items to this restaurant. Please create your own restaurant in order to delete items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Item deleted.")
        return redirect(url_for('showMenu', sportCategory_id=sportCategory_id))
    else:
        return render_template('deleteSportItem.html', item=itemToDelete, sportCategory_id=sportCategory_id)
    # return "This page is for deleting sporting item item %s" % menu_id


# jsonify sport category
@app.route('/category/JSON')
def sportcategoryJSON():
    sportcategory = session.query(SportCategory).all()
    return jsonify(sportcategory=[s.serialize for s in sportcategory])


@app.route('/category/<int:sportCategory_id>/menu/JSON')
def sportMenuJSON(sportCategory_id):
    sportcategory = session.query(SportCategory).filter_by(id=sportCategory_id).one()
    items = session.query(SportingItem).filter_by(
        sport_cat_id=sportCategory_id).all()
    return jsonify(SportingItem=[i.serialize for i in items])


@app.route('/category/<int:sportCategory_id>/menu/<int:menu_id>/JSON')
def sportItemJSON(sportCategory_id, menu_id):
    Sport_Item = session.query(SportingItem).filter_by(id=menu_id).one()
    return jsonify(Sport_Item=Sport_Item.serialize)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)