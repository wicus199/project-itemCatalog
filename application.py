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

# Add a category -- Methods: GET, POST
@app.route('/catalog/add/', methods=['GET','POST'])
def addCategory():
    if request.method == 'POST':
        newCat = Category(
            name=request.form['itemName'],
            description=request.form['description'],
            url=request.form['pic_url'])
        session.add(newCat)
        session.commit()
        return redirect(url_for('catalog'))
    else:
        return render_template('addCategory.html')

# View the contents of a category -- Methods: GET
@app.route('/catalog/<int:category_id>/')
def viewCategory(category_id):
    # Query the items in a category
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return render_template('category.html', category=category, itemList=items)

# Edit a category -- Methods: GET, POST
@app.route('/catalog/<int:category_id>/edit/', methods=['GET','POST'])
def editCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        category.name = request.form['itemName']
        category.description = request.form['description']
        category.url = request.form['pic_url']
        session.add(category)
        session.commit()
        return redirect(url_for('viewCategory', category_id=category.id))
    else:
        return render_template('editCategory.html', category=category)

# Delete a category -- Methods: GET, POST
@app.route('/catalog/<int:category_id>/delete/', methods=['GET','POST'])
def deleteCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(category)
        session.commit()
        return redirect(url_for('catalog'))
    else:
        return render_template('deleteCategory.html', category=category)

# View an item -- Methods: GET
@app.route('/catalog/<int:category_id>/item/<int:item_id>/')
def viewItem(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('items.html', category=category, item=item)

# Create a new item inside a category -- Methods: GET, POST
@app.route('/catalog/<int:category_id>/add/', methods=['GET','POST'])
def addItem(category_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    cat_id = request.form.get('cat-name')
    if request.method == 'POST':
        newItem = Item(
            name = request.form['itemName'],
            description = request.form['description'],
            url = request.form['pic_url'],
            category_id = int(cat_id)
        )
        session.add(newItem)
        session.commit()
        #returns to the page of the selected category of the new item
        return redirect(url_for('viewCategory', category_id=int(cat_id)))
    else:
        return render_template('addItem.html', category=category, categories=categories)

# Edit an item -- Methods: GET, POST
@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit/', methods=['GET','POST'])
def editItem(category_id, item_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()

    cat_id = request.form.get('cat-name')

    if request.method == 'POST':
        item.name = request.form['itemName']
        item.description = request.form['description']
        item.url = request.form['pic_url']
        item.category_id = request.form.get('cat-name')    #request.form.get('')
        session.add(item)
        session.commit()
        return redirect(url_for('viewItem', category_id=cat_id, item_id=item.id))
    else:
        return render_template('editItem.html', categories=categories, category=category, item=item)

# Delete an item -- Methods: GET, POST
@app.route('/catalog/<int:category_id>/item/<int:item_id>/delete/', methods=['GET','POST'])
def deleteItem(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('viewCategory', category_id=category.id))
    else:
        return render_template('deleteItem.html', category=category, item=item)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)