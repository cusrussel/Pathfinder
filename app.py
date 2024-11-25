from flask import Flask, request, jsonify, render_template, Response,  redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
import pickle
import pandas as pd
import hashlib
from pprint import pprint
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from flask_mail import Mail, Message
import firebase_admin
from firebase_admin import credentials, db, initialize_app


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

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


app = Flask(__name__)

app.secret_key = os.environ.get('APP_SECRET_KEY')
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
            return redirect(url_for("admin_dashboard"))
        else:
            # Show an alert and reload the login page
            return render_template('admin/login.html') + '''
                <script>
                    alert("Authentication failed. Please try again.");
                </script>
            '''
    
    # If GET request, show login form
    return render_template('admin/login.html')

#Route for Admin Login
@app.route('/admin')
def admin():
    return render_template('/admin/login.html')

#Route for admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('/admin/dashboard.html')

# MODIFIED QUESTIONNAIRE
@app.route('/modify-questions')
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
    model_path = "decision_tree_model.pkl"
    with open(model_path, "rb") as file:
        model = pickle.load(file)
    return model

model = load_model()

print( model.feature_names_in_)

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

def get_programs():
    ref = db.reference('programs')  # Assuming your programs are stored under the 'programs' node
    programs = ref.get()  # Retrieve all the programs from the database
    return programs

@app.route('/programs')
def programs():
    ref = db.reference('programs')  # Reference the 'programs' node in Firebase Realtime Database
    programs = ref.get()  # This will return a list of programs
    
    # If the structure is a dictionary, loop through it and format it into a list
    program_list = [{"program_id": idx, "name": program['name'], "category": program['categories'], "image_url": program['image_url']} 
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


@app.route('/manage-programs')
def manage_programs():
    ref = db.reference('programs')  # Reference the 'programs' node in Firebase Realtime Database
    programs = ref.get()  # This will return a list of programs
    
    # If the structure is a dictionary, loop through it and format it into a list
    program_list = [{"program_id": idx, "name": program['name'], "degree":program['degree'], "miniDescription": program['miniDescription'], "overview": program['overview'], "skills": program['skills'], "strengths": program['strengths'], "weaknesses": program['weaknesses'], "category": program['categories'], "image_url": program['image_url'], "benefits": program['benefits'], "career_paths": program["career_paths"], "conclusion": program["conclusion"]} 
                    for idx, program in enumerate(programs)]
    
    return render_template('/admin/manage-programs.html', programs=program_list)

# Route to get a single program for editing

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
    categories = json.loads(data['categories'])  # Convert the string to a list
    image = request.files.get('image')  # Get the uploaded image file

    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image.save(os.path.join(UPLOAD_FOLDER, filename))  # Save the image to the static folder
        image_url = f'uploads/{filename}'  # Store the relative path

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
            'categories': categories,
            'image_url': image_url  # Store the relative image URL
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
        image_url = f'uploads/{filename}'
        program['image_url'] = image_url  # Update the image URL in the database

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



@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        print("Received Data:", data)

        user_strand = data.get('strand', None)

        strand_program_map = {
            'STEM': [
                'BS in Accountancy', 
                'BS in Architecture', 
                'BS in Civil Engineering', 
                'BS in Computer Engineering', 
                'BS in Computer Science',
                'BS in Electronic Engineering',  # Comma added here
                'BS in Education', 
                'BS in Information Technology', 
                'BS in Mathematics', 
                'BS in Mechanical Engineering', 
                'BS in Nursing',
                'BS in Statistics'
            ],
            'ABM': [
                'BS in Accountancy',
                'BS in Business Administration', 
                'BS in Business Marketing', 
                'BS in Entrepreneur',
                'BS in Education',
                'BS in Hospitality Management',
                'BS in Public Administration',  # Comma added here
                'BS in Tourism Management'
            ],
            'HUMSS': [
                'AB in Communication', 
                'AB in Multimedia Arts', 
                'AB in Political Science',
                'BA in Sociology',
                'BS in Criminology',
                'BS in Education',
                'BS in Political Science',
                'AB in Psychology'
            ],
            'TVL Track': [
                'BS in Culinary Arts',
                'BS in Computer Science',
                'BS in Information Technology',
                'BS in Hospitality Management',
                'BS in Tourism Management'
            ],
            'None': [
                'BS in Accountancy', 
                'BS in Architecture', 
                'BS in Civil Engineering', 
                'BS in Computer Engineering', 
                'BS in Computer Science',
                'BS in Electronic Engineering',  # Comma added here
                'BS in Education', 
                'BS in Information Technology', 
                'BS in Mathematics', 
                'BS in Mechanical Engineering', 
                'AB in Psychology',  # Comma added here
                'BS in Nursing',
                'BS in Statistics',
                'BS in Accountancy',
                'BS in Business Administration', 
                'BS in Business Marketing', 
                'BS in Entrepreneur',
                'BS in Hospitality Management',
                'BS in Public Administration',  # Comma added here
                'BS in Tourism Management',
                'AB in Communication', 
                'AB in Multimedia Arts', 
                'AB in Political Science',
                'BA in Sociology',
                'BS in Criminology',
                'BS in Political Science',
                'BS in Culinary Arts',
            ]
        }
        
        user_data = process_data(data)
        user_df = pd.DataFrame([user_data])
        user_df = user_df[model.feature_names_in_]

        proba = model.predict_proba(user_df)[0]
        classes = model.classes_
        
        print("Raw probabilities and classes:", list(zip(classes, proba * 100)))

        top_indices = proba.argsort()[::-1]
        filtered_predictions = [
            (classes[i], proba[i] * 100) for i in top_indices 
            if classes[i] in strand_program_map.get(user_strand, [])
        ]
        top_3_predictions = filtered_predictions[:3]

        response = {
            'top_3_predictions': [
                {'category': pred[0], 'probability': round(pred[1])} for pred in top_3_predictions
            ]
        }
        print("Filtered Top 3 Predictions:", response['top_3_predictions'])

        return jsonify(response)
    except Exception as e:
        print(f"Error processing prediction: {e}")
        return jsonify({'error': str(e)}), 500




def process_data(data):

    mappings = {
    "sex": {
        "Male": 12.95,
        "Female": 10.971,
        'Prefer not to say': 2.5
    },

    "income": {
        "Less than 9,100 to 18,200": 11.764,
        "18,200 to 109,200": 11.606,
        "109,200 to 182,000 and above": 12.5
    },

    "personality": {
        "ISTJ": 11.333,
        "ISFJ": 16.909,
        "INFJ": 8.889,
        "INTJ": 10.5,
        "ISTP": 22,
        "ISFP": 9.062,
        "INFP": 10.167,
        "INTP": 14.773,
        "ESTP": 12.125,
        "ESFP": 0,
        "ENFP": 8.615,
        "ENTP": 18,
        "ESTJ": 9.5,
        "ESFJ": 14.938,
        "ENFJ": 12.5,
        "ENTJ": 10.765,
        
    },

    "strand":{
        "ABM": 8,
        "STEM": 13.8,
        "HUMMS": 9.312,
        "TVL Track": 15.407,
        "None": 10.526,
    },

    "specialized_subj": {  # Combined mapping for specialized subjects
        "Business Math": 6.222, 
        "Fundamentals of Accounting": 1, 
        "Business and Management": 2, 
        "Applied Economics": 7, 
        "Organization and Management": 12.4, 
        "Business Finance": 5, 
        "Business Ethics and Social Responsibility": 5, 
        "Business Marketing": 9.6, 
        "Business Enterprise Simulation": 10.167,

        "Calculus": 14.636, 
        "General Physics": 6, 
        "General Chemistry": 7.8, 
        "General Biology": 18.625, 
        "Research/Capstone Project": 12.692,

        "Philippine Politics and Governance": 11.615, 
        "Creative Writing / Malikhaing Pagsulat": 16.5, 
        "Creative Nonfiction: The Literacy Essay": 16,
        "Disciplines and Ideas in the Social Sciences": 6.455, 
        "Disciplines and Ideas in the Applied Social Sciences": 11.5, 
        "Introduction to World Religions and Belief System": 14, 
        "Trends, Networks and Critical Thinking in the 21st Century Culture": 9.333, 
        "Community Engagement, Solidarity and Citizenship": 7.833
    },

    "specialization": {
        "Cookery": 16.867, 
        "ICT/CSS": 13.583, 
        "default": 11.108,
    },

    "core_subj": {
        "Oral Communication": 0, 
        "Reading and Writing Skills": 6.333, 
        "21st Century Literature from the Philippines and the World": 2, 
        "Komunikasyon at Pananaliksik sa Wika at Kulturang Pilipino": 0, 
        "Pagbasa at Pagsusuri ng Iba't ibang Teksto Tungo sa Pananaliksik": 12, 
        "Introduction to the Philosophy of the Human Person/ Pambungad sa Pilosopiya ng Tao": 5, 
        "General Mathematics": 19, 
        "Statistics and Probability": 17, 
        "Contemporary Philippine Arts from the Regions": 8, 
        "Earth and Life Science": 16, 
        "Physical Science": 10, 
        "Media and Information Literacy": 7.429, 
        "Personal Delopment/Pansariling Kaunlaran": 12, 
        "Physical Education and Health": 21
    },

    "p_skill":{
        "Technical and Analytical Skills": 15.882,
        "Creative Skills": 7,
        "Leadership and Management Skills":16.133,
        "Communication Skills": 8,
        "Collaboration and Teamwork": 11.571,
        "Practical and Hands-On Skills": 13.75,
        "Business and Entrepreneurial Skills": 9.273,
        "Languages and Cultural Understanding": 12.444,
        "Health and Wellness Skills": 14.25,
        "Digital Literacy": 11.409
    },

    "s_skill":{
        "Technical and Analytical Skills": 12.667,
        "Creative Skills": 6.647,
        "Leadership and Management Skills":12.455,
        "Communication Skills": 13.828,
        "Collaboration and Teamwork": 11.067,
        "Practical and Hands-On Skills": 14.385,
        "Business and Entrepreneurial Skills": 10,
        "Languages and Cultural Understanding": 8,
        "Health and Wellness Skills": 9.75,
        "Digital Literacy": 12.263
    },

    "interests1":{
        "Talking/Presenting in front of people": 11.947,
        "Drawing and creating digital designs": 8.613,
        "Managing a business": 11.031,
        "Learning things about technology": 14.189,
        "Physical ang Health Activities": 12.37
    },

    "interests2":{
        "Interactive with people": 9.933,
        "Editing Videos": 6.842,
        "Organizing large-scale events": 15,
        "Solving math problems": 13.316,
        "Taking care of others": 12.5
    },

    "interests3":{
        "Performing on stage": 12.609,
        "Dealing with designs of buildings/infrastructures": 8.167,
        "Analyzing financial data": 12.86,
        "Programming": 13.435,
        "Helping others learn": 11.167
    },

    "interests4":{
        "Reading/Writing content": 11.097,
        "Cooking and presenting dishes": 11.769,
        "Studying political systems": 9.696,
        "Dealing with human behavior": 10.905,
        "Traveling": 14.735
    }



}
    # Convert categorical data to numerical values using mappings
    processed_data = {}

    # Convert 'sex' to numerical: 0 for Female, 1 for Male
    processed_data['sex'] = mappings['sex'].get(data['sex'], -1)

    # Convert 'income'
    processed_data['income'] = mappings['income'].get(data['income'], -1)

    processed_data['personality'] = mappings['personality'].get(data['personality'], -1)

    # Convert 'strand'
    processed_data['strand'] = mappings['strand'].get(data['strand'], -1)

    # Convert 'specialized_subj'
    processed_data['specialized_subj'] = mappings['specialized_subj'].get(data['specialized_subj'], -1)

    # Convert 'specialization'
    processed_data['specialization'] = mappings['specialization'].get(data['specialization'], mappings['specialization']['default'])

    # Convert 'core_subj'
    processed_data['core_subj'] = mappings['core_subj'].get(data['core_subj'], -1)

    processed_data['p_skill'] = mappings['p_skill'].get(data['p_skill'], -1)

    processed_data['s_skill'] = mappings['s_skill'].get(data['s_skill'], -1)

    processed_data['interests1'] = mappings['interests1'].get(data['interests1'], -1)

    processed_data['interests2'] = mappings['interests2'].get(data['interests2'], -1)

    processed_data['interests3'] = mappings['interests3'].get(data['interests3'], -1)

    processed_data['interests4'] = mappings['interests4'].get(data['interests4'], -1)


    return processed_data

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
