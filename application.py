# Import flask package
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database import Base, Category, Item
from flask import session as login_session
import random
import string

import httplib2
import json
import requests

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogDatabase')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Main catalog page -- Methods: GET
@app.route('/')
@app.route('/catalog/')
def catalog():
    # Query all categories to display main_catalog
    main_catalog = session.query(Category).all()
    # Pass main_catalog to catalog.html page (main page) into catalog_items
    return render_template('catalog.html', catalog_items=main_catalog)

# # Add a category -- Methods: GET, POST
# @app.route('/catalog/add/')
# def addCategory():
#     return

# View the contents of a category -- Methods: GET
@app.route('/catalog/<int:category_id>/')
def viewCategory(category_id):
    # Query the items in a category
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return render_template('category.html', category=category, itemList=items)

# # Edit a category -- Methods: GET, POST
# @app.route('/catalog/<int:category_id>/edit/')
# def editCategory():
#     return
#
# # Delete a category -- Methods: GET, POST
# @app.route('/catalog/<int:category_id>/delete/')
# def deleteCatagory():
#     return
#
# View an item -- Methods: GET
@app.route('/catalog/<int:category_id>/item/<int:item_id>/')
def viewItem(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('items.html', category=category, item=item)

# # Create a new item inside a category -- Methods: GET, POST
# @app.route('/catalog/<int:category_id>/add/')
# def createNewItem():
#     return
#
# # Edit an item -- Methods: GET, POST
# @app.route('/catalog/<int:category_id>/item/<int:item_id>/edit/')
# def editItem():
#     return
#
# # Delete an item -- Methods: GET, POST
# @app.route('/catalog/<int:category_id>/item/<int:item_id>/delete/')
# def deleteItem():
#     return

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)