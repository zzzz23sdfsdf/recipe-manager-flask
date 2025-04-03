from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import uuid
import random

app = Flask(__name__)

DATA_FILE = "static/recipes.json"

# Load recipes from JSON file
def load_recipes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            if isinstance(data, dict):
                return data
    return {}

# Save recipes to JSON file
def save_recipes(recipes):
    with open(DATA_FILE, "w") as file:
        json.dump(recipes, file, indent=4)

@app.route("/")
def home():
    recipes = list(load_recipes().values())  # Load all recipes
    random_recipes = random.sample(recipes, min(3, len(recipes)))  # Pick 3 random recipes
    return render_template("index.html", recipes=random_recipes)

@app.route("/api/recipes")
def api_recipes():
    recipes = list(load_recipes().values())
    return jsonify(recipes)

@app.route("/search")
def search():
    query = request.args.get("query", "").strip()
    query = query.replace("+", " ")  # Handle URL-encoded spaces
    
    search_type = request.args.get("type", "general").strip()
    recipes = load_recipes().values()
    results = []
    
    query_lower = query.lower()
    numeric_part = None
    
    # Precise prep time search
    if search_type == 'prep_time':
        results = [
            recipe for recipe in recipes 
            if query == str(recipe.get("prep_time", "")).replace(" minutes", "")
        ]
        return render_template("search_results.html", query=query, search_type=search_type, results=results, count=len(results))
    
    # Precise servings search
    elif search_type == 'servings':
        results = [
            recipe for recipe in recipes 
            if query == str(recipe.get("servings", "")).replace(" people", "")
        ]
        return render_template("search_results.html", query=query, search_type=search_type, results=results, count=len(results))
    
    # Check for numeric part in query
    if any(c.isdigit() for c in query):
        numeric_part = ''.join(c for c in query if c.isdigit())

    for recipe in recipes:
        match_found = False
        
        # Time-based search (handling different minute formats)
        if numeric_part and ("minute" in query_lower or "min" in query_lower or "mins" in query_lower):
            prep_time = str(recipe.get("prep_time", "")).lower()
            
            if any(prep_time.startswith(f"{numeric_part} {t}") for t in ["minute", "min", "mins", "min."]):
                results.append(recipe)
                match_found = True
                continue
            
            # Extract just the number from prep_time and compare
            prep_digits = ''.join(c for c in prep_time if c.isdigit())
            if prep_digits == numeric_part:
                results.append(recipe)
                match_found = True
                continue

        # General search across title, summary, ingredients, etc.
        if not match_found:
            searchable_text = [
                recipe.get("title", "").lower(),
                recipe.get("summary", "").lower(),
                str(recipe.get("prep_time", "")).lower(),
                str(recipe.get("servings", "")).lower(),
                f"{recipe.get('servings', '')} people"
            ]

            if recipe.get("ingredients"):
                for name, amount in recipe["ingredients"].items():
                    searchable_text.append(name.lower())
                    searchable_text.append(str(amount).lower())

            searchable_text.append(recipe.get("allergy_info", "").lower())

            if recipe.get("Cooking Tips"):
                searchable_text.append(recipe.get("Cooking Tips", "").lower())

            if recipe.get("Steps"):
                searchable_text.extend([str(step).lower() for step in recipe.get("Steps", [])])

            if recipe.get("nutrition"):
                for key, value in recipe["nutrition"].items():
                    searchable_text.append(f"{key}: {value}".lower())

            all_text = " ".join(filter(None, searchable_text))

            if query_lower in all_text:
                results.append(recipe)

    return render_template("search_results.html", query=query, search_type=search_type, results=results, count=len(results))
@app.route("/view/<id>")
def view_recipe(id):
    recipes = load_recipes()
    recipe = recipes.get(id)
    if not recipe:
        # Debug information
        print(f"Recipe not found. ID: {id}")
        print(f"Available IDs: {list(recipes.keys())}")
        return render_template("recipe_not_found.html", id=id)
    
    # Extract numeric part of prep_time for search link
    prep_time_num = ''.join(c for c in str(recipe.get("prep_time", "")) if c.isdigit())
    
    return render_template("view.html", recipe=recipe, prep_time_num=prep_time_num)

@app.route("/add", methods=["GET"])
def add_recipe():
    return render_template("add_recipe.html")

@app.route("/add", methods=["POST"])
def add_recipe_post():
    # Ensure this route is only called via AJAX (from navbar)
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"success": False, "error": "Unauthorized access"}), 403

    recipes = load_recipes()
    
    # Find the next sequential ID
    existing_ids = [int(id) for id in recipes.keys() if id.isdigit()]
    new_id = str(max(existing_ids) + 1) if existing_ids else str(len(recipes) + 1)

    # Get JSON data from the request
    data = request.get_json()
    
    # Comprehensive error tracking
    errors = {}

    # Validate and sanitize each field
    # Title validation
    title = data.get("title", "").strip()
    if not title:
        errors["title"] = "Recipe title is required"

    # Summary validation
    summary = data.get("summary", "").strip()
    if not summary:
        errors["summary"] = "Recipe summary is required"

    # Preparation time validation
    try:
        prep_time = data.get("prep_time", "").replace(" minutes", "").strip()
        prep_time_mins = int(prep_time)
        if prep_time_mins <= 0:
            errors["prep_time"] = "Preparation time must be a positive number"
    except (ValueError, TypeError):
        errors["prep_time"] = "Invalid preparation time"

    # Servings validation
    try:
        servings = int(data.get("servings", "").strip())
        if servings <= 0:
            errors["servings"] = "Servings must be a positive number"
    except (ValueError, TypeError):
        errors["servings"] = "Invalid number of servings"

    # Ingredients validation
    ingredients_raw = data.get("ingredients", "").strip()
    if not ingredients_raw:
        errors["ingredients"] = "Ingredients are required"
    else:
        try:
            ingredients = {}
            ingredient_items = ingredients_raw.split(",")
            for item in ingredient_items:
                item = item.strip()
                if not item:
                    continue
                parts = item.split(":")
                if len(parts) != 2:
                    errors["ingredients"] = "Ingredients must be in 'name: amount' format"
                    break
                name = parts[0].strip()
                amount = parts[1].strip()
                if not name or not amount:
                    errors["ingredients"] = "Each ingredient must have a name and amount"
                    break
                ingredients[name] = amount
        except Exception:
            errors["ingredients"] = "Invalid ingredients format"

    # Optional numeric fields with validation
    try:
        calories = int(data.get("calories", "0").strip()) if data.get("calories", "").strip() else 0
        if calories < 0:
            errors["calories"] = "Calories must be a non-negative number"
    except (ValueError, TypeError):
        errors["calories"] = "Invalid calories value"

    try:
        protein = int(data.get("protein", "0").strip()) if data.get("protein", "").strip() else 0
        if protein < 0:
            errors["protein"] = "Protein must be a non-negative number"
    except (ValueError, TypeError):
        errors["protein"] = "Invalid protein value"

    # If there are any errors, return them
    if errors:
        return jsonify({
            "success": False, 
            "errors": errors
        }), 400

    # Prepare recipe object
    new_recipe = {
        "id": new_id,
        "title": title,
        "summary": summary,
        "prep_time": f"{prep_time_mins} minutes",
        "servings": servings,
        "ingredients": ingredients,
        "allergy_info": data.get("allergy_info", "").strip(),
        "nutrition": {
            "Calories": calories, 
            "Protein": protein
        },
        "Cooking Tips": data.get("tips", "").strip(),
        "Steps": [step.strip() for step in data.get("Steps", "").split("\n") if step.strip()],
        "image_url": data.get("image_url", "").strip(),
    }

    # Save the new recipe
    recipes[new_id] = new_recipe
    save_recipes(recipes)
    
    # Return success response
    return jsonify({
        "success": True, 
        "id": new_id
    })

@app.route("/edit/<id>", methods=["GET"])
def edit_recipe(id):
    recipes = load_recipes()
    if id not in recipes:
        return "Recipe not found", 404
    return render_template("edit_recipe.html", recipe=recipes[id])

@app.route("/edit/<id>", methods=["POST"])
def edit_recipe_post(id):
    recipes = load_recipes()
    if id not in recipes:
        return "Recipe not found", 404

    title = request.form.get("title", "").strip()
    summary = request.form.get("summary", "").strip()
    prep_time = request.form.get("prep_time", "").strip()
    servings = request.form.get("servings", "").strip()
    ingredients_raw = request.form.get("ingredients", "").strip()
    allergy_info = request.form.get("allergy_info", "").strip()
    calories = request.form.get("calories", "").strip()
    protein = request.form.get("protein", "").strip()
    cooking_tips = request.form.get("cooking_tips", "").strip()
    image_url = request.form.get("image_url", "").strip()
    steps_raw = request.form.get("Steps", "").strip()

    if not title or not summary or not prep_time or not servings or not ingredients_raw:
        return "Error: All fields are required", 400

    ingredients = {}
    for item in ingredients_raw.split(","):
        item = item.strip()
        if not item:
            continue
        parts = item.split(":")
        if len(parts) != 2:
            return "Error: Ingredients should be in format 'name: amount'", 400
        ingredients[parts[0].strip()] = parts[1].strip()

    steps = [step.strip() for step in steps_raw.split("\n") if step.strip()]

    try:
        servings = int(servings)
        calories = int(calories) if calories else recipes[id]["nutrition"]["Calories"]
        protein = int(protein) if protein else recipes[id]["nutrition"]["Protein"]
    except ValueError:
        return "Error: Numeric fields must contain valid numbers.", 400

    recipes[id] = {
        "id": id,
        "title": title,
        "summary": summary,
        "prep_time": f"{prep_time} minutes",
        "servings": f"{servings} people",
        "ingredients": ingredients,
        "allergy_info": allergy_info,
        "nutrition": {"Calories": calories, "Protein": protein},
        "Cooking Tips": cooking_tips,
        "Steps": steps,
        "image_url": image_url,
    }

    save_recipes(recipes)
    return redirect(url_for("view_recipe", id=id))

@app.route("/delete/<id>", methods=["POST"])
def delete_recipe(id):
    recipes = load_recipes()
    if id in recipes:
        del recipes[id]
        save_recipes(recipes)
        
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"status": "success", "redirect": url_for("home")})
        
        return redirect(url_for("home"))
    
    return "Recipe not found", 404

if __name__ == "__main__":
    app.run(debug=True, port=5001)