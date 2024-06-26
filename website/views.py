from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import BMI, Note
from . import db
import json
import requests  # Import the requests library


views = Blueprint('views', __name__)

# Function to make API call
def get_calories_burned(activity):
    api_url = "https://api.api-ninjas.com/v1/caloriesburned?activity="
    api_key = "+8B6pELyu/5ydbMwwsAqIg==SPOaULMXs4LbZSgx"
    headers = {"Authorization": "Bearer " + api_key}
    response = requests.get(api_url + activity, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None

@views.route('/', methods=['GET', 'POST'])
@login_required
def bmi():
    if request.method == 'POST':
        weight = request.form.get('weight')
        height = request.form.get('height')
        age = request.form.get('age')
        gender = request.form.get("gender")
        selected_muscle = request.form.get("muscle")  # Get selected muscle from the form

        if len(weight) < 1:
            flash('Weight is too short!', category='error')
        elif len(height) < 1:
            flash('Height is too short!', category='error')
        elif len(age) < 1:
            flash('Age is too short!', category='error')
        else:
            calculated_bmi = (int(weight) / (int(height) * int(height))) * 10000
            new_bmi = BMI(weight=weight, height=height, age=age, user_id=current_user.id)
            db.session.add(new_bmi)
            db.session.commit()
            flash('BMI added!', category='success')

            if selected_muscle:
                # If a muscle is selected, make the API call
                api_response = get_calories_burned(selected_muscle)
                if api_response:
                    print("Calories burned:", api_response)
                    # You can process the API response as needed

    return render_template("home.html", user=current_user)


#This function is used to add a note to the database
def home():
    if request.method == 'POST':
        note = request.form.get('note')#Gets the note from the HTML

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note
            db.session.add(new_note) #adding the note to the database
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
