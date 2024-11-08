from flask import Flask, request, jsonify, render_template, Response
import pickle
import pandas as pd
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
app = Flask(__name__)


app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
app.config['MAIL_DEBUG'] = True  # Set to False in production

mail = Mail(app)

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
    return render_template('recommender.html')

@app.route('/analysis')
def analysis():
    return render_template('analytics.html')

@app.route('/programs')
def programs():
    return render_template('programs.html')

# PROGRAMS ROUTES

@app.route('/programs/accountancy')
def accountancy():
    return render_template('/programs/accountancy.html')

@app.route('/programs/architecture')
def architecture():
    return render_template('/programs/architecture.html')

@app.route('/programs/business-administration')
def businessadministration():
    return render_template('/programs/business-administration.html')

@app.route('/programs/business-management')
def businessmanagement():
    return render_template('/programs/business-management.html')

@app.route('/programs/civil-engineering')
def civilengineering():
    return render_template('/programs/civil-engineering.html')

@app.route('/programs/communication')
def communication():
    return render_template('/programs/communication.html')

@app.route('/programs/criminology')
def criminology():
    return render_template('/programs/criminology.html')

@app.route('/programs/computer-engineering')
def computerengineering():
    return render_template('/programs/computer-engineering.html')

@app.route('/programs/computer-science')
def computerscience():
    return render_template('/programs/computer-science.html')

@app.route('/programs/culinary-arts')
def culinaryarts():
    return render_template('/programs/culinary-arts.html')

@app.route('/programs/education')
def education():
    return render_template('/programs/education.html')

@app.route('/programs/electronic-engineering')
def electronicengineering():
    return render_template('/programs/electronic-engineering.html')

@app.route('/programs/entrepreneurship')
def entrepreneurship():
    return render_template('/programs/entrepreneur.html')

@app.route('/programs/hospitality-management')
def hospitalitymanagement():
    return render_template('/programs/hospitality-management.html')

@app.route('/programs/information-technology')
def informationtechnology():
    return render_template('/programs/information-technology.html')

@app.route('/programs/mathematics')
def mathematics():
    return render_template('/programs/mathematics.html')

@app.route('/programs/mechanical-engineering')
def mechanicalengineering():
    return render_template('/programs/mechanical-engineering.html')

@app.route('/programs/multimedia-arts')
def multimediaarts():
    return render_template('/programs/multimedia-arts.html')

@app.route('/programs/nursing')
def nursing():
    return render_template('/programs/nursing.html')

@app.route('/programs/political-science')
def politicalscience():
    return render_template('/programs/political-science.html')

@app.route('/programs/psychology')
def psychology():
    return render_template('/programs/psychology.html')

@app.route('/programs/public-administration')
def publicadministration():
    return render_template('/programs/public-administration.html')

@app.route('/programs/sociology')
def sociology():
    return render_template('/programs/sociology.html')

@app.route('/programs/statistics')
def statistics():
    return render_template('/programs/statistics.html')

@app.route('/programs/tourism-management')
def tourismmanagement():
    return render_template('/programs/tourism-management.html')



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
