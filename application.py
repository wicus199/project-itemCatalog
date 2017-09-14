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

# Main catalog page
@app.route('/')
@app.route('/catalog/')
def catalog():
    # Query all categories to display main_catalog
    main_catalog = session.query(Category).all()
    # Pass main_catalog to catalog.html page (main page) into catalog_items
    return render_template('catalog.html', catalog_items=main_catalog)

# Create a new catalog category
@app.route('/catagory/new/')
def createNewCategory():
    return

# View the contents of a category
@app.route('/catagory/<int:catagory_id>/')
def viewCategory():
    return

# Edit a catagory
@app.route('/catagory/<int:catagory_id>/edit/')
def editCategory():
    return

# Delete a category
@app.route('/catagory/<int:catagory_id>/delete/')
def deleteCatagory():
    return

# Create a new item inside a category
@app.route('/catagory/<int:catagory_id>/new/')
def createNewItem():
    return

# View an item
@app.route('/catagory/<int:catagory_id>/item/<int:item_id>/')
def viewItem():
    return

# Edit an item
@app.route('/catagory/<int:catagory_id>/item/<int:item_id>/edit/')
def editItem():
    return

# Delete an item
@app.route('/catagory/<int:catagory_id>/item/<int:item_id>/delete')
def deleteItem():
    return