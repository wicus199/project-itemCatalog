## Synopsis

This project forms part of the Full Stack Web developer Nanodegree from Udacity. For the project, the goal was to design a website with the following minimum functionality:
* The website should have items listed in categories. The items and categories should be queried from a database.
* Registered users should be able to add, edit and delete items in categories with the use of forms. 
* Users should be able to register on the website using 3rd party providers like Google and Facebook.  
* Only owners of items (the user that created the item) should be able to edit and delete the item. 
* Users of the website that are not registered should only be able to view the items.
* The website should have JSON endpoints that give the same information as the HTML endpoints. 
* Code should be neatly formatted, well commented and python code should be compliant with the Python PEP 8 style guide.

Some extra functionality 
* There exists an administrator account that can create, edit and delete categories as well. 
* Normal registered users do not have permission to add, edit and delete categories, only items.
* The admin account is also the owner of all the items added in the database, thus admin can edit and delete any item.

## Motivation

The motivation behind this project was to learn how to develop a RESTful web application using the Flask framework and learning how to implement third-party Oauth authentication.
Experience in using HTTP methods and learning how these methods relate to CRUD operations was also obtained. Creating and interacting with databases was the main focus of this 
project and valuable real life experience was gained while doing this.

The project also required a full-stack design. An aesthetically pleasing responsive frontend was designed to compliment the backend. This provided valuable experience in full-stack 
web development.  

## Website description

The landing page of the website is a page that displays all the categories present in the database. These categories can only be created, edited and deleted by the administrator of the site.
Clicking on a category takes the user to a page that displays all the items present in that category. Clicking on an item renders a page that shows the title and description of the item. If 
the user is logged in, the user will be able to click the **Add Item** button when viewing the contents of a category. This will present a form to the user, asking the user for the following:
* Item name
* Item description 
* Item image URL (Default image is provided if user does not supply URL)
* Drop down menu containing all the categories in the database. This selects the category of the newly created item. 

If the user is not logged in when clicking the **Add Item** button, the user will be redirected to the login page to first log in before being able to add items to his/her account.

When viewing an item, if the user is the creator of the item, **Edit Item** and **Delete Item** buttons will be visible to the user. This allows the user to edit or delete the item.
If the user is not the creator of the item, the buttons won't be visible.

The **Edit Item** form is identical to the **Add Item** form, with the only difference being that the fields are populated with the existing item's data. Clicking the submit button 
from this form or the **Add Item** form will redirect the user back to the category selected in the form. 

When clicking the **Delete Item** button, the user will be redirected to a page asking if they are sure they want to delete. If **Yes** is selected, the item is removed from the database
and the user is redirected to the category from where the item was deleted. 

The administrator of the website is able to add, edit and delete categories in addition to items. The process works exactly the same as the CRUD operations for items explained above. When logged
into the administrator account, the **Add Category** button is visible on the landing (main) page. When viewing the contents of a category, the **Edit Category** and **Delete Category**
buttons are visible to the administrator. The administrator also has the ability to edit and delete any item in the database. 

## Installation

The code was developed for python version 3.6.1 in windows 10. This was not tested in Mac OS X or Linux. This will **NOT** work for python 2.7.1
To be able to run the application, install python 3.6.x by downloading python from [here](https://www.python.org/downloads/) and running the setup file. 

The following python packages were used: 
* Flask
* sqlalchemy
* Developed and tested on Windows 10 using pyCharm community edition

## API Reference

The website contains the following JSON endpoints that contains the same info as the HTML endpoints:

* View all the categories in the catalog: /catalog/json
* View category information: /catalog/<int:category_id>/json
* View items in a category: /catalog/<int:category_id>/items/json
* View item information: /catalog/<int:category_id>/item/<int:item_id>/json

## Tests

To test website functionality, perform the following steps:
1. Open application.py in a python editor and run using python 3.6.1 interpreter. Alternatively, run the application by opening a command prompt in the project root directory
where application.py is located and enter **python application.py** in the console. This will run the app.
2. Open your browser (Chrome was used for testing) and visit localhost:5000/ or localhost:5000/catalog. This will open the homepage
