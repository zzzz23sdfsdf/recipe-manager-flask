# Healthy Recipe Finder-flask

A Flask-based web application for managing and discovering recipes with a clean, intuitive user interface.
![image](https://github.com/user-attachments/assets/b36d1bd5-bf13-4548-8b47-6d6f509522bc)

Features

Recipe Management: Create, view, edit, and delete recipes
Search Functionality: Find recipes by name, ingredients, or category
Responsive Design: Works seamlessly across desktop and mobile devices
JSON Data Storage: Lightweight data persistence using JSON files
Clean UI: Modern interface with intuitive navigation

Technologies Used

Backend: Python, Flask
Frontend: HTML, CSS, JavaScript
Data Storage: JSON
Dependencies: flask, uuid, json

Project Structure
Copyrecipe-manager/
├── server.py              # Main Flask application
├── static/                # Static files
│   ├── recipes.json       # Recipe data storage
│   ├── script.js          # Frontend JavaScript
│   └── style.css          # CSS styling
└── templates/             # HTML templates
    ├── add_recipe.html    # Add new recipe form
    ├── base.html          # Base template layout
    ├── edit_recipe.html   # Edit recipe form
    ├── index.html         # Homepage
    ├── search_results.html# Search results page
    └── view.html          # Recipe details view
    
Installation & Setup

Clone the repository:
Copygit clone https://github.com/yourusername/recipe-manager.git
cd recipe-manager

Create and activate a virtual environment (optional but recommended):
Copypython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:
Copypip install -r requirements.txt

Run the application:
Copypython server.py

Open your browser and navigate to:
Copyhttp://localhost:5000


Usage
Adding a Recipe

Click the "Add Recipe" button on the homepage
Fill in the recipe details including title, ingredients, instructions, and category
Click "Save" to add the recipe to your collection

Searching for Recipes

Enter a search term in the search bar
Results will display recipes matching the name, ingredients, or category

Editing a Recipe

Navigate to the recipe you want to edit
Click the "Edit" button
Modify the recipe details
Click "Save" to update the recipe

Deployment
This application can be deployed on various platforms:
Render

Create a new Web Service on Render
Connect to your GitHub repository
Set the build command: pip install -r requirements.txt
Set the start command: python server.py
