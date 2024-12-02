from flask import Flask, request, jsonify, render_template, Response, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
import pickle
import pandas as pd
from datetime import datetime
from flask_mail import Mail, Message
import firebase_admin
from firebase_admin import credentials, db, initialize_app
from pprint import pprint
import hashlib
import os
import json
from functools import wraps

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pickle

from datetime import datetime
import pytz

import warnings
warnings.filterwarnings('ignore')

#Import algorithms
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, ConfusionMatrixDisplay
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import export_graphviz

import category_encoders as ce
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from dotenv import load_dotenv

load_dotenv()

firebase_credentials_str = os.environ.get('FIREBASE_CREDENTIALS')
database_url = os.environ.get('FIREBASE_DATABASE_URL')


# Check if environment variables are set
if not firebase_credentials_str:
    raise ValueError("FIREBASE_CREDENTIALS environment variable not set.")
if not database_url:
    raise ValueError("FIREBASE_DATABASE_URL environment variable not set.")

# Load credentials from the JSON string
firebase_credentials = json.loads(firebase_credentials_str)

# Initialize Firebase app with credentials and database URL
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred, {
    'databaseURL': database_url
})

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            # Redirect to the login page if not authenticated
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

UPLOAD_FOLDER_CSV = 'uploads/csv'  # For storing uploaded CSV files
UPLOAD_FOLDER_MODEL = 'uploads/models'  # For storing trained models

os.makedirs(UPLOAD_FOLDER_CSV, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_MODEL, exist_ok=True)


app = Flask(__name__)

app.secret_key = os.environ.get('APP_SECRET_KEY')
app.config['UPLOAD_FOLDER_CSV'] = UPLOAD_FOLDER_CSV
app.config['UPLOAD_FOLDER_MODEL'] = UPLOAD_FOLDER_MODEL
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
app.config['MAIL_DEBUG'] = True  # Set to False in production

mail = Mail(app)

# Logging Admin Account
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Hash the submitted password to compare it with the stored hashed password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Retrieve the stored admin credentials from Realtime Database
        ref = db.reference('admin')
        admin_data = ref.get()

        # Check if the provided username and password match the stored ones
        if admin_data and admin_data.get('username') == username and admin_data.get('password') == hashed_password:
            session['admin_logged_in'] = True  # Set session variable
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template('admin/login.html') + '''
                <script>
                    alert("Authentication failed. Please try again.");
                </script>
            '''

    return render_template('admin/login.html')

#Route for Admin Login
@app.route('/admin')
def admin():
    return render_template('/admin/login.html')

#Route for admin Dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

#Route for admin Reports
@app.route('/admin/reports')
@admin_required
def admin_reports():
    return render_template('admin/reports.html')

#ROUTE FOR ADMIN UPLOAD 
@app.route('/admin/upload')
@admin_required
def admin_upload():
    # Fetch data from Firebase Realtime Database
    ref = db.reference('uploads')  # Reference to the 'uploads' node
    uploads_data = ref.get()  # Get all the data under 'uploads'

    # If there is data, sort it by date and time (date first, then time)
    if uploads_data:
        # Sort by date and time
        sorted_uploads = sorted(uploads_data.items(), key=lambda x: (x[1]['date'], x[1]['time']), reverse=True)
        uploads_data = dict(sorted_uploads)  # Rebuild the dictionary with sorted data

    # Pass the sorted data with date and time to the frontend template
    return render_template('admin/upload.html', uploads=uploads_data)


#ROUTE FOR ADMIN SETTINGS
@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    ref = db.reference('admin')
    admin_data = ref.get()

    if request.method == 'POST':
        username = request.form['username']
        current_password = request.form['current_password']
        new_password = request.form['new_password']

        if admin_data and username == admin_data.get('username'):
            # Hash the current password and compare it to the stored hashed password
            hashed_current_password = hashlib.sha256(current_password.encode()).hexdigest()
            if hashed_current_password == admin_data.get('password'):
                # Hash the new password and update it in the database
                hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
                ref.update({'password': hashed_new_password})
                return jsonify({"success": True, "message": "Password updated successfully!"}), 200
            else:
                return jsonify({"success": False, "message": "Current password is incorrect."}), 400
        else:
            return jsonify({"success": False, "message": "Admin user not found."}), 404

    return render_template('admin/settings.html', admin_info=admin_data)

# MODIFIED QUESTIONNAIRE
@app.route('/admin/modify-questions')
@admin_required
def questions():
    ref = db.reference('questions')  # Reference the 'questions' node in Realtime Database
    questions = ref.get()  # This will return a list of questions
    
    # If the structure is a list, loop through it
    question_list = [{"question_id": idx, "question": question['question'], "options": question['options']} 
                    for idx, question in enumerate(questions)]
    
    return render_template('/admin/modify-questionnaire.html', questions=question_list)

# Route to get a single question
@app.route('/get_question/<question_id>', methods=['GET'])
def get_question(question_id):
    ref = db.reference(f'questions/{question_id}')  # Reference to a specific question
    question = ref.get()  # Get the question data
    if question:
        return jsonify(question)  # Return the question data as JSON
    return jsonify({"error": "Question not found"}), 404

#add questions
@app.route('/add_question', methods=['POST'])
def add_question():
    data = request.get_json()

    # References
    question_ref = db.reference('questions')  # Reference to the questions node
    counter_ref = db.reference('counters/questions')  # Reference to the counter for questions

    # Get the current list of questions
    questions = question_ref.get() or []  # Get the current list or an empty list if none exist

    # Get the current max index from the counter
    current_index = counter_ref.get() or 0
    new_index = current_index + 1

    # Update the counter
    counter_ref.set(new_index)

    # Create the new question entry
    new_question = {
        'question_id': new_index,
        'question': data['question'],
        'data-field': data['data_field'],
        'options': [{'label': option, 'value': option} for option in data['options']]
    }

    # Append the new question to the list
    questions.append(new_question)

    # Update the questions list in Firebase
    question_ref.set(questions)

    # Return the newly created question ID
    return jsonify({"message": "Question added successfully", "question_id": new_index}), 201

#update questions
@app.route('/update_question/<question_id>', methods=['PUT'])
def update_question(question_id):
    data = request.get_json()
    question_ref = db.reference(f'questions/{question_id}')  # Reference to the specific question
    question_ref.update({
        'question': data['question'],
        'options': [{'label': option, 'value': option} for option in data['options']],
        'data_field': data['data_field']  # Update the dataField in the database
    })
    return jsonify({"message": "Question updated successfully"}), 200

#delete questions
@app.route('/delete_question/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    try:
        question_ref = db.reference('questions')
        counter_ref = db.reference('counters/questions')

        # Fetch all questions
        questions = question_ref.get() or []

        # Find the question with the provided ID
        question_to_delete = next((q for q in questions if q['question_id'] == question_id), None)

        if not question_to_delete:
            return jsonify({"error": f"Question with ID {question_id} not found"}), 404

        # Remove the question from the list
        questions.remove(question_to_delete)

        # If the list is empty after deletion, reset everything
        if not questions:
            question_ref.set([])
            counter_ref.set(0)
            return jsonify({"message": "Question deleted and database is now empty."}), 200

        # Reindex the questions and update the question_id inside each question object
        for idx, question in enumerate(questions, 0):
            question['question_id'] = idx  # Update the question_id

        # Save the updated questions list back to Firebase
        question_ref.set(questions)

        # Decrement the counter
        current_counter = counter_ref.get() or 0
        counter_ref.set(current_counter - 1)

        return jsonify({"message": "Question deleted and reindexed successfully"}), 200

    except Exception as e:
        # Log the error
        print(f"Error in delete_question: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.errorhandler(404)
def page_not_found(e):
    # Redirect to the home page
    return redirect(url_for('home'))

#LOADS THE ML MODEL
def load_model():
    # Path to the models folder
    models_folder = 'uploads/models'
    
    # Get the list of files in the models folder
    model_files = os.listdir(models_folder)
    
    # Filter the files to get only the ones with a .pkl extension
    model_files = [file for file in model_files if file.endswith('.pkl')]
    
    # If there are no model files, return an error or default message
    if not model_files:
        raise FileNotFoundError("No model file found in the models folder.")
    
    # Sort files to get the most recent model (based on modification time)
    model_files.sort(key=lambda x: os.path.getmtime(os.path.join(models_folder, x)), reverse=True)
    
    # Get the path to the most recent model file
    latest_model_path = os.path.join(models_folder, model_files[1])
    
    # Load and return the most recent model
    with open(latest_model_path, "rb") as file:
        model = pickle.load(file)
    
    return model

model = load_model()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/recommender')
def recommender():
    # Fetch questions directly for rendering
    ref = db.reference('questions')  # Reference the 'questions' node
    counter_ref = db.reference('counters/questions')
    questions = ref.get() 

    total_questions = counter_ref.get()  # Get the total number of questions from Firebase
    session['total_questions'] = total_questions or 0

    return render_template('recommender.html', questions=questions, total_questions=session['total_questions'])

@app.route('/analysis')
def analysis():
    return render_template('analytics.html')

@app.route('/api/programs', methods=['GET'])
def get_programs():
    # Fetch programs as JSON from Firebase
    refs = db.reference('programs')
    programs = refs.get()

    program_list = [{ "miniDescription": program['miniDescription'], 
                    "name": program['name'], "image_url": program['image_url'], 
                    "logo_url": program['logo_url']} for program in programs]

    return jsonify({'programs': program_list})

@app.route('/programs')
def programs():
    ref = db.reference('programs')  # Reference the 'programs' node in Firebase Realtime Database
    programs = ref.get()  # This will return a list of programs
    
    # If the structure is a dictionary, loop through it and format it into a list
    program_list = [{"program_id": idx, "name": program['name'], "category": program['categories']} 
                    for idx, program in enumerate(programs)]
    return render_template('programs.html',  programs=program_list)

@app.route('/programs/<program_name>')
def program_details(program_name):
    # Reference to the 'programs' node in Firebase
    programs_ref = db.reference('programs')
    
    # Fetch all programs
    programs = programs_ref.get()
    
    if not programs:
        return "No programs found in the database", 404
    
    # Find the matching program by name
    matched_program = None
    if isinstance(programs, list):  # If programs is a list
        for program in programs:
            # Check if the 'name' field matches the program_name
            if 'name' in program and program['name'].lower() == program_name.lower():
                matched_program = program
                break
    elif isinstance(programs, dict):  # If programs is a dictionary
        for key, program in programs.items():
            # Check if the 'name' field matches the program_name
            if 'name' in program and program['name'].lower() == program_name.lower():
                matched_program = program
                break
    
    if not matched_program:
        return "Program not found", 404  # Return an error if no matching program is found
    
    # Extract the required details from the matched program
    program_details = {
        "name": matched_program['name'] if 'name' in matched_program else 'N/A',
        "degree": matched_program['degree'] if 'degree' in matched_program else 'N/A',
        "miniDescription": matched_program['miniDescription'] if 'miniDescription' in matched_program else 'N/A',
        "overview": matched_program['overview'] if 'overview' in matched_program else 'N/A',
        "skills": matched_program['skills'] if 'skills' in matched_program else [],
        "strengths": matched_program['strengths'] if 'strengths' in matched_program else [],
        "weaknesses": matched_program['weaknesses'] if 'weaknesses' in matched_program else [],
        "benefits": matched_program['benefits'] if 'benefits' in matched_program else [],
        "career_paths": matched_program['career_paths'] if 'career_paths' in matched_program else [],
        "conclusion": matched_program['conclusion'] if 'conclusion' in matched_program else [],
        "image_url": matched_program['image_url'] if 'image_url' in matched_program else 'N/A',
    }

    # Pass the program details and program name to the template
    return render_template('dynamic-programs.html', program=program_details, program_name=program_name)


@app.route('/admin/manage-programs')
@admin_required
def manage_programs():
    ref = db.reference('programs')  # Reference the 'programs' node in Firebase Realtime Database
    programs = ref.get()  # This will return a list of programs
    
    # If the structure is a dictionary, loop through it and format it into a list
    program_list = [{"program_id": idx, "name": program['name'], "degree":program['degree'], "miniDescription": program['miniDescription'], "overview": program['overview'], "skills": program['skills'], "strengths": program['strengths'], "weaknesses": program['weaknesses'], "category": program['categories'], "image_url": program['image_url'], "logo_url": program['logo_url'], "benefits": program['benefits'], "career_paths": program["career_paths"], "conclusion": program["conclusion"]} 
                    for idx, program in enumerate(programs)]
    
    return render_template('/admin/manage-programs.html', programs=program_list)

# Route to get a single program for editing

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/get_program/<program_id>', methods=['GET'])
def get_program(program_id):
    ref = db.reference(f'programs/{program_id}')  # Reference to a specific program
    program = ref.get()  # Get the program data
    if program:
        return jsonify(program)  # Return the program data as JSON
    return jsonify({"error": "Program not found"}), 404

@app.route('/add_program', methods=['POST'])
def add_program():
    data = request.form  # For image upload, use form instead of JSON

    # Log to check if data is received correctly
    print("Form data:", data)
    
    program_name = data['name']
    miniDescription = data['miniDescription']
    degree = data['degree']
    overview = data['overview']
    categories = json.loads(data['categories'])  # Convert the string to a list
    image = request.files.get('image')  # Get the uploaded image file
    logo = request.files.get('logo')  # Get the uploaded logo file
    skills = json.loads(data['skills'])
    strengths = json.loads(data['strengths'])
    weaknesses = json.loads(data['weaknesses'])
    benefits = json.loads(data['benefits'])
    career_paths = json.loads(data['career_paths'])
    conclusion = data['conclusion']

    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_FOLDER, filename))  # Save the image to the static folder
        image_url = f'uploads/{filename}'  # Store the relative path

        # Handle the logo upload (if any)
        logo_url = None
        if logo and allowed_file(logo.filename):
            logo_filename = secure_filename(logo.filename)
            logo.save(os.path.join(UPLOAD_FOLDER, logo_filename))
            logo_url = f'uploads/{logo_filename}'  # Store the relative path to the logo

        # References
        program_ref = db.reference('programs')  # Reference to the programs node
        counter_ref = db.reference('counters/programs')  # Reference to the counter for programs

        # Get the current list of programs
        programs = program_ref.get() or []

        # Get the current max index from the counter
        current_index = counter_ref.get() or 0
        new_index = current_index + 1

        # Update the counter
        counter_ref.set(new_index)

        # Create the new program entry
        new_program = {
            'program_id': new_index,
            'name': program_name,
            'miniDescription': miniDescription,
            'degree': degree,
            'overview': overview,
            'categories': categories,
            'skills': skills,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'benefits': benefits,
            'career_paths': career_paths,
            'conclusion': conclusion,
            'image_url': image_url,  # Store the relative image URL
            'logo_url': logo_url  # Store the relative logo URL
        }

        # Append the new program to the list
        programs.append(new_program)

        # Update the programs list in Firebase
        program_ref.set(programs)

        return jsonify({"message": "Program added successfully", "program_id": new_index}), 201
    else:
        return jsonify({"error": "Invalid file format. Only images are allowed."}), 400

@app.route('/update_program/<int:program_id>', methods=['PUT'])
def update_program(program_id):
    data = request.form  # For image upload, use form instead of JSON

    # Ensure required fields are present
    required_fields = ['name', 'degree', 'miniDescription', 'overview', 'categories', 'skills', 'strengths', 'weaknesses', 'benefits', 'career_paths', 'conclusion']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing field: {field}"}), 400

    program_name = data['name']
    miniDescription = data['miniDescription']
    degree = data['degree']
    overview = data['overview']
    categories = json.loads(data['categories'])  # Convert the string to a list
    image = request.files.get('image')  # Get the uploaded image file (optional)
    logo = request.files.get('logo')  # Get the uploaded logo file (optional)
    skills = json.loads(data['skills'])
    strengths = json.loads(data['strengths'])
    weaknesses = json.loads(data['weaknesses'])
    benefits = json.loads(data['benefits'])
    career_paths = json.loads(data['career_paths'])
    conclusion = data['conclusion']

    # Retrieve the program from the database
    program_ref = db.reference(f'programs/{program_id}')
    program = program_ref.get()

    if not program:
        return jsonify({"message": "Program not found"}), 404

    # Handle the image upload (if any)
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_FOLDER, filename))
        image_url = f'/static/uploads/{filename}'
        program['image_url'] = image_url  # Update the image URL in the database

    # Handle the logo upload (if any)
    if logo and allowed_file(logo.filename):
        logo_filename = secure_filename(logo.filename)
        logo.save(os.path.join(UPLOAD_FOLDER, logo_filename))
        logo_url = f'/static/uploads/{logo_filename}'  # Store the relative path to the logo
        program['logo_url'] = logo_url  # Update the logo URL in the database

    # Update other fields
    program['name'] = program_name
    program['categories'] = categories
    program['skills'] = skills
    program['strengths'] = strengths
    program['weaknesses'] = weaknesses
    program['miniDescription'] = miniDescription
    program['overview'] = overview
    program['degree'] = degree
    program['benefits'] = benefits
    program['career_paths'] = career_paths
    program['conclusion'] = conclusion

    # Update the program in the database
    program_ref.set(program)

    return jsonify({"message": "Program updated successfully"}), 200


# Route to delete a program
@app.route('/delete_program/<int:program_id>', methods=['DELETE'])
def delete_program(program_id):
    try:
        program_ref = db.reference('programs')  # Reference to the programs node
        counter_ref = db.reference('counters/programs')  # Reference to the counter for programs

        # Fetch all programs
        programs = program_ref.get() or []

        # Find the program with the provided ID
        program_to_delete = next((p for p in programs if p['program_id'] == program_id), None)

        if not program_to_delete:
            return jsonify({"error": f"Program with ID {program_id} not found"}), 404

        # Remove the program from the list
        programs.remove(program_to_delete)

        # If the list is empty after deletion, reset everything
        if not programs:
            program_ref.set([])  # Reset the programs list
            counter_ref.set(0)  # Reset the counter for programs
            return jsonify({"message": "Program deleted and database is now empty."}), 200

        # If there was an associated image, delete it
        if 'image_url' in program_to_delete:
            image_path = os.path.join('static', program_to_delete['image_url'])
            if os.path.exists(image_path):
                os.remove(image_path)

        # Reindex the programs and update the program_id inside each program object
        for idx, program in enumerate(programs, 0):
            program['program_id'] = idx  # Update the program_id

        # Save the updated programs list back to Firebase
        program_ref.set(programs)

        # Update the counter
        current_counter = counter_ref.get() or 0
        counter_ref.set(current_counter - 1)

        return jsonify({"message": "Program deleted and reindexed successfully"}), 200

    except Exception as e:
        # Log the error
        print(f"Error in delete_program: {e}")
        return jsonify({"error": str(e)}), 500
    
# PROGRAMS ROUTES


@app.route('/send-email', methods=['POST'])
def send_email():
    
    try:
        # Fetch all users from the Realtime Database
        ref = db.reference('users')
        users = ref.get()

        # Get the latest user by key
        if users:
            latest_user_key = sorted(users.keys())[-1]  # Get the last key in the sorted list
            latest_user = users[latest_user_key]

            # Extract the output values from the latest user document
            output1 = latest_user.get('output_1')
            output2 = latest_user.get('output_2')
            output3 = latest_user.get('output_3')
        else:
            output1, output2, output3 = None, None, None

        # Compose email content
        email = request.form.get('email')
        subject = "Your Recommended College Programs"
        body = f"""
Dear {email},

After analyzing your input and preferences, our system has generated the following recommendations to best suit your needs:

1. {output1}

2. {output2}

3. {output3}: 

We’re here to support you every step of the way, we look forward to seeing your journey unfold!

Warm regards,
Pathfinder
"""

        # Send email
        msg = Message(subject, recipients=[email])
        msg.body = body
        mail.send(msg)
        return Response(status=204)

    except Exception as e:
        return f"Failed to send email: {str(e)}"


@app.route('/api/demographic', methods=['GET'])
def get_demographic_data():
    try:
        # Reference the 'users' node in your Firebase database
        users_ref = db.reference('users')
        users_data = users_ref.get()  # Fetch all user data

        # Initialize a dictionary to count users by sex
        data = {}
        
        # Iterate through the user data
        if users_data:
            for user in users_data.values():
                gender = user.get('sex')  # Get the sex of the user
                
                # Increment the count for this gender
                if gender in data:
                    data[gender] += 1
                else:
                    data[gender] = 1

        return jsonify(data), 200  # Return JSON with HTTP 200 status code

    except Exception as e:
        return jsonify({"error": str(e)}), 500 

@app.route('/api/demographicPercentage', methods=['GET'])
def get_demographic_data_percentage():
    try:
        # Reference the 'users' node in your Firebase database
        users_ref = db.reference('users')
        users_data = users_ref.get()  # Fetch all user data

        # Initialize a dictionary to count users by sex
        data = {}
        total_users = 0
        
        # Iterate through the user data
        if users_data:
            for user in users_data.values():
                gender = user.get('sex')  # Get the sex of the user
                
                # Increment the count for this gender
                if gender in data:
                    data[gender] += 1
                else:
                    data[gender] = 1
                
                total_users += 1  # Count the total number of users

        # Calculate percentages
        if total_users > 0:
            for gender in data:
                percentage = (data[gender] / total_users) * 100
                data[gender] = {
                    "count": data[gender],
                    "percentage": round(percentage, 2)  # Round to 2 decimal places
                }

        return jsonify(data), 200  # Return JSON with HTTP 200 status code

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error if something goes wrong

@app.route('/api/user_count', methods=['GET'])
def get_total_user_count():
    try:
        # Reference the 'users' node in your Firebase database
        users_ref = db.reference('users')
        users_data = users_ref.get()  # Fetch all user data

        # Count the total number of users
        total_users = len(users_data) if users_data else 0

        return jsonify({"total_users": total_users}), 200  # Return JSON with HTTP 200 status code

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error if something goes wrong


@app.route('/api/strand', methods=['GET'])
def get_strand():
    try:
        # Reference the 'users' node in your Firebase database
        users_ref = db.reference('users')
        users_data = users_ref.get()  # Fetch all user data

        # Initialize a dictionary to count users per strand
        data = {}

        # Total number of users
        total_users = 0

        # Iterate through the user data
        if users_data:
            for user in users_data.values():
                strand = user.get('strand')  # Get the strand of the user
                total_users += 1  # Increment total user count
                
                # Increment the count for this strand
                if strand in data:
                    data[strand] += 1
                else:
                    data[strand] = 1

        # Calculate the percentage for each strand and round to 2 decimals
        if total_users > 0:
            for strand in data:
                percentage = round((data[strand] / total_users) * 100, 2)  # Calculate percentage
                data[strand] = percentage  # Append percentage symbol

        return jsonify(data), 200  # Return JSON with HTTP 200 status code

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error if something goes wrong

@app.route('/api/strandPercentage', methods=['GET'])
def get_strandPercentage():
    try:
        # Reference the 'users' node in your Firebase database
        users_ref = db.reference('users')
        users_data = users_ref.get()  # Fetch all user data

        # Initialize a dictionary to count users per strand
        data = {}

        # Total number of users
        total_users = 0

        # Iterate through the user data
        if users_data:
            for user in users_data.values():
                strand = user.get('strand')  # Get the strand of the user
                total_users += 1  # Increment total user count

                # Increment the count for this strand
                if strand in data:
                    data[strand] += 1
                else:
                    data[strand] = 1

        # Calculate the percentage for each strand and format with a '%' symbol
        if total_users > 0:
            for strand in data:
                percentage = round((data[strand] / total_users) * 100, 2)  # Calculate percentage
                data[strand] = f"{percentage}%"  # Format as a string with a percentage symbol

        return jsonify(data), 200  # Return JSON with HTTP 200 status code

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error if something goes wrong
    
@app.route('/api/strands', methods =['GET'])
def get_strands():
    try:
        # Reference the 'users' node in your Firebase database
        users_ref = db.reference('users')
        users_data = users_ref.get()  # Fetch all user data

        # Initialize a dictionary to count users per strand
        data = {}

        # Iterate through the user data
        if users_data:
            for user in users_data.values():
                strand = user.get('strand')  # Get the strand of the user
                
                # Increment the count for this strand
                if strand in data:
                    data[strand] += 1
                else:
                    data[strand] = 1

        return jsonify(data), 200  # Return JSON with HTTP 200 status code

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error if something goes wrong
    
@app.route('/api/data', methods=['GET'])
def get_chart_data():
    strand_filter = request.args.get('strand', 'All')  # Default to 'All' if no filter is provided
    
    try:
        # Reference the 'users' node in your Firebase database
        users_ref = db.reference('users')
        users_data = users_ref.get()  # Fetch all user data

        # Initialize a dictionary to hold the aggregated data
        data = {}

        # Process each user's data
        if users_data:
            for user in users_data.values():
                strand = user.get('strand')
                # Check if strand matches the filter
                if strand_filter != 'All' and strand != strand_filter:
                    continue  # Skip this user if strand does not match

                # Aggregate counts for output_1, output_2, and output_3
                for output in ['output_1', 'output_2', 'output_3']:
                    program = user.get(output)
                    if program:
                        if program not in data:
                            data[program] = {}

                        # Increment the user count for this strand and program
                        if strand in data[program]:
                            data[program][strand] += 1
                        else:
                            data[program][strand] = 1

        return jsonify(data), 200  # Return JSON with HTTP 200 status code

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error if something goes wrong

@app.route('/api/percentage', methods=['GET'])
def get_chart_percentage():
    strand_filter = request.args.get('strand', 'All').strip()  # Normalize input to remove extra spaces

    try:
        # Reference the 'users' node in your Firebase database
        users_ref = db.reference('users')
        users_data = users_ref.get()  # Fetch all user data

        # Initialize variables for the filtered data
        program_counts = {}
        total_in_strand = 0

        # Process each user's data
        if users_data:
            for user in users_data.values():
                # Normalize strand and program names for comparison
                strand = user.get('strand', '').strip()
                program = user.get('output_1', '').strip()

                # Skip users without strand or program data
                if not strand or not program:
                    continue

                # Normalize case to ensure matching is case-insensitive
                if strand_filter.lower() != 'all' and strand.lower() != strand_filter.lower():
                    continue

                # Count the total users in the filtered strand
                total_in_strand += 1

                # Count occurrences of each program
                if program in program_counts:
                    program_counts[program] += 1
                else:
                    program_counts[program] = 1

        # Avoid division by zero
        if total_in_strand == 0:
            return jsonify({"error": "No users found for the selected strand"}), 404

        # Calculate percentages for each program
        program_percentages = {
            program: round((count / total_in_strand) * 100, 2)
            for program, count in program_counts.items()
        }

        return jsonify(program_percentages), 200  # Return JSON with HTTP 200 status code

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error if something goes wrong

@app.route('/submit', methods=['POST'])
def submit():
    now = datetime.now()
    data = request.get_json()  # Assuming this returns a dictionary

    print("Data received:", data)
    print("Strand:", data.get('strand')) 

    print("Current date and time:", now)

    try:
        # Set up the reference path in Firebase where you want to store this data
        ref = db.reference('users')  # 'users' will be the root node
        
        # Push data to Firebase
        ref.push({
            "sex": data.get("sex"),
            "strand": data.get("strand"),
            "output_1": data.get("output_1"),
            "output_2": data.get("output_2"),
            "output_3": data.get("output_3"),
            "timestamp": now.isoformat()  # Optionally add a timestamp
        })
        
        print("Data added to Firebase successfully")

    except Exception as e:
        print(f"The error '{e}' occurred")
        return jsonify({"error": str(e)}), 500

    return "Data submission complete", 200



@app.route('/retrain', methods=['GET', 'POST'])
def retrain():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        filepath_csv = os.path.join(app.config['UPLOAD_FOLDER_CSV'], file.filename)
        file.save(filepath_csv)

        philippine_tz = pytz.timezone('Asia/Manila')
        now = datetime.now(pytz.utc)
        now_ph = now.astimezone(philippine_tz)
        date = datetime.utcnow().strftime('%Y-%m-%d')
        time = now_ph.strftime(' %I:%M:%S %p')
        
        ref = db.reference('uploads')
        new_entry = ref.push({
            'file_path': file.filename,
            'date': date,
            'time': time
        })

        df = pd.read_csv(filepath_csv)
        df.drop('Timestamp', axis=1, inplace=True)
        df.drop('Would you like your future college program to be related to your current track/strand?', axis=1, inplace=True)
        df.drop('Which university are you planning to attend for college? (If college student, please enter your current university)', axis=1, inplace=True)

        df['specialized_subj'] = df['In which specialized subject do you have the highest grade?'].combine_first(df['In which specialized subject do you have the highest grade?.1']).combine_first(df['In which specialized subject do you have the highest grade?.2'])
        df = df.drop(columns=['In which specialized subject do you have the highest grade?', 'In which specialized subject do you have the highest grade?.1', 'In which specialized subject do you have the highest grade?.2'])

        cols = df.columns.tolist()
        cols.insert(cols.index('Which track/strand are you part of?') + 1, cols.pop(cols.index('specialized_subj')))
        df = df[cols]

        df.fillna("Not Applicable", inplace=True)
        df.columns = ['sex', 'income', 'personality', 'strand', 'specialized_subj', 'specialization', 'core_subj', 'p_skill', 's_skill', 'interests1', 'interests2', 'interests3', 'interests4', 'program']

        def clean_columns(df, columns):
            for column in columns:
                df[column] = df[column].str.replace(r'\s*\(.*?\)\s*', '', regex=True)
            return df

        def strip_columns(df, columns):
            for column in columns:
                df[column] = df[column].str.strip()
            return df

        columns_to_clean = ['personality', 'p_skill', 's_skill']
        columns_to_strip = ['interests1', 'interests2', 'interests3', 'interests4']
        df = clean_columns(df, columns_to_clean)
        df = strip_columns(df, columns_to_strip)

        le = LabelEncoder()
        df['program_encoded'] = le.fit_transform(df['program'])

        # Save the LabelEncoder
        label_encoder_path = os.path.join(app.config['UPLOAD_FOLDER_MODEL'], 'label_encoder.pkl')
        with open(label_encoder_path, 'wb') as f:
            pickle.dump(le, f)

        # Dynamic mappings
        columns_to_map = ['sex', 'income', 'personality', 'strand', 'specialized_subj', 'specialization', 'core_subj', 'p_skill', 's_skill', 'interests1', 'interests2', 'interests3', 'interests4']
        
        dynamic_mappings = {}
        for column in columns_to_map:
            mean_encoded = df.groupby(column)['program_encoded'].mean().round(3).to_dict()
            dynamic_mappings[column] = mean_encoded
        
        mappings_filepath = os.path.join(app.config['UPLOAD_FOLDER_MODEL'], 'mappings.json')
        with open(mappings_filepath, 'w') as f:
            json.dump(dynamic_mappings, f)

        df_features = df.drop('program', axis=1)
        for column, mean_encoded in dynamic_mappings.items():
            df_features[column] = df_features[column].map(mean_encoded)

        X = df_features.iloc[:, :-1]
        y = df_features.iloc[:, -1]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestClassifier()
        model.fit(X_train, y_train)

        model_filename = os.path.join(app.config['UPLOAD_FOLDER_MODEL'], 'random_forest_model.pkl')
        with open(model_filename, "wb") as file:
            pickle.dump(model, file)

        return jsonify({"success": True, "message": "Model retrained and mappings generated successfully!"}), 200
    else:
        return jsonify({"success": False, "message": "Failed"}), 400
    

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        print("Received Data:", data)

        user_strand = data.get('strand', None).lower()  # Convert to lowercase for consistency

        # Fetch program data dynamically from Firebase
        programs_ref = db.reference('programs')  # Adjust path to match your Firebase structure
        programs = programs_ref.get() or []  # Default to empty list if nothing is retrieved

        if not isinstance(programs, list):
            raise ValueError("Expected a list of programs from Firebase.")

        # Create dynamic strand_program_map
        strand_program_map = {}
        for program in programs:  # Iterate directly over the list
            program_name = program.get('name', '').strip()
            categories = program.get('categories', [])
            
            if program_name and isinstance(categories, list):
                for category in categories:
                    category = category.lower().strip()
                    strand_program_map.setdefault(category, []).append(program_name)

        print("Dynamic strand_program_map:", strand_program_map)

        # Load label encoder and mappings
        label_encoder_path = os.path.join(app.config['UPLOAD_FOLDER_MODEL'], 'label_encoder.pkl')
        with open(label_encoder_path, 'rb') as f:
            label_encoder = pickle.load(f)

        mappings_filepath = os.path.join(app.config['UPLOAD_FOLDER_MODEL'], 'mappings.json')
        with open(mappings_filepath, 'r') as f:
            dynamic_mappings = json.load(f)

        # Process user data
        user_data = process_data(data, dynamic_mappings)
        user_df = pd.DataFrame([user_data])
        user_df = user_df[model.feature_names_in_]

        # Predict probabilities
        proba = model.predict_proba(user_df)[0]
        classes = model.classes_

        # Decode the predicted classes
        decoded_classes = label_encoder.inverse_transform(classes)

        print("Decoded probabilities and classes:", list(zip(decoded_classes, proba * 100)))

        # Filter and return top predictions based on strand
        top_indices = proba.argsort()[::-1]
        if user_strand is None or user_strand.lower() == 'none':  # Include all programs if no strand is specified
            filtered_predictions = [(decoded_classes[i], proba[i] * 100) for i in top_indices]
        else:  # Filter predictions based on the user's strand
            user_strand = user_strand.lower()
            filtered_predictions = [
                (decoded_classes[i], proba[i] * 100) for i in top_indices
                if decoded_classes[i] in strand_program_map.get(user_strand, [])
            ]
        top_3_predictions = filtered_predictions[:3]

        response = {
            'top_3_predictions': [
                {'category': pred[0], 'probability': round(pred[1])} for pred in top_3_predictions
            ],
            'top_3_programs': [pred[0] for pred in top_3_predictions]
        }
        return jsonify(response)
    except Exception as e:
        print(f"Error processing prediction: {e}")
        return jsonify({'error': str(e)}), 500


def process_data(data, mappings):
    processed_data = {}

    for column, mapping in mappings.items():
        if column == 'program':
            processed_data[column] = data.get(column)  # Keep the program as categorical (do not map)
        else:
            processed_data[column] = mapping.get(data.get(column), -1)  # Use mean encoding for other columns

    return processed_data

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
