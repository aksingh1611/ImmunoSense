from flask import Flask, render_template, request, redirect, url_for, session, jsonify 
from pymongo import MongoClient
from datetime import datetime
import pickle
from email_utils import send_email
from otp_utils import generate_numeric_otp

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = '17d7df82bc707d15ef69bd259a67c2e7d48e46a53abe80f9'

sender_mail = 'immunosence@gmail.com'
sender_password = 'mbvt tobm fmjl bmld'

def verify_otp(entered_otp, expected_otp):
    return entered_otp == expected_otp

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database']
users_collection = db['users']

prediction_collection = db['prediction_results']

# Load the machine learning model and scaler
model = pickle.load(open('C:\Users\Ashutosh\ImmunoSense - Copy\xgb_model.pkl', 'rb'))
# scaler = pickle.load(open('scaler.pickle', 'rb'))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/otpVerify", methods=["GET","POST"])
def Otp_page():
    if request.method == "POST":
        user_otp = request.form.get("otp")
        otp = session.get('otp')  
        if verify_otp(user_otp, otp):
            # Clear OTP from session after successful verification
            session.pop("otp", None)
            # Get the email from session
            email = session.get("email")
            FirstName = session.get("FirstName")
            LastName = session.get("LastName")
            password = session.get("password")
            
            user_data = {
            "email": email,
            "FirstName": FirstName,
            "LastName": LastName,
            "password": password,
            }
            
            users_collection.insert_one(user_data)
            
            return redirect(url_for('index'))
        else:
             "Invalid OTP. Please try again."  
    
    return render_template("Otp_page.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        FirstName = request.form.get("FirstName")
        LastName = request.form.get("LastName")
        password = request.form.get("password")
        
        otp = generate_numeric_otp()
        subject = "IMMUNOSENSE || REGISTRATION"
        message = "Hey {} your OTP is {}. \nThankyou.".format(FirstName,otp)
        send_email(sender_mail,sender_password,email,subject,message)
        
        #  redirect to page where you take otp input in the form from the user
        session['otp'] = otp
        session['email'] = email
        session['FirstName'] = FirstName
        session['LastName'] = LastName
        session['password'] = password
        
        return redirect(url_for('Otp_page'))
        
    return render_template("registration.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    user = users_collection.find_one({"email": email, "password": password})
    if user:
        session['email'] = email
        return redirect(url_for('prediction'))
    else:
        return "Invalid email or password"

@app.route("/prediction", methods=["GET", "POST"])
def prediction():
    if 'email' in session:
        if request.method == "POST":
            # Get the input values from the form
            height_str = request.form.get('height')
            weight_str = request.form.get('weight')
            protein_score_str = request.form.get('protein')
            average_age_str = request.form.get('age')
            diabetes_level_str = request.form.get('diabetes')
            sleep_hours_str = request.form.get('sleep')
            
            # Check if any of the form fields are empty
            if not all([height_str, weight_str, protein_score_str, average_age_str, diabetes_level_str, sleep_hours_str]):
                return render_template('prediction.html', prediction_text="Please fill out all the fields.")
            
            # Convert input values to appropriate data types
            try:
                height = float(height_str)
                weight = float(weight_str)
                protein_score = float(protein_score_str)
                average_age = float(average_age_str)
                diabetes_level = float(diabetes_level_str)
                sleep_hours = float(sleep_hours_str)
            except ValueError:
                return render_template('prediction.html', prediction_text="Invalid input values. Please provide numeric values.")
            
            # Function to calculate BMI
            def calculate_bmi(height, weight):
                bmi = weight / ((height / 100) ** 2)
                return bmi
            
            # Calculate BMI
            bmi = calculate_bmi(height, weight)
            
            # Use the model to predict the immunity index
            pred = model.predict([[bmi, protein_score, average_age, diabetes_level, sleep_hours]])
            immunity_index = pred[0]
            
            # Add immunity index message based on the prediction
            if immunity_index > 40:
                message = "Your immunity index is Good! Healthy Diet, Regular Exercise, Adequate Sleep, Stress Management, Hydration. Avoid Smoking and Limit Alcohol. Regular Health Check-ups, Stay Informed"
            elif 25 <= immunity_index <= 40:
                message = "Your immunity index is moderate! Balanced Diet, Hydration, Avoid Smoking and Limit Alcohol, Regular Exercise, Adequate Sleep, Stress Management. Immune-Boosting Foods and Supplements, Good Hygiene Practices. Regular Health Check-ups, Stay Informed"
            else:
                message = "Your immunity index is poor! Nutritious Diet, Supplements, Regular Exercise, Quit Smoking, Stress Management, Limit Alcohol, Good Hygiene Practices, Adequate Sleep. Avoid Exposure to Illness, Medical Check-up, Stay Informed"
            
            # Save prediction result to MongoDB
            user_email = session['email']
            prediction_data = {
                "email": user_email,
                "prediction_result": message,
                "immunity_index": immunity_index,
                "prediction_date": datetime.now()
            }
            prediction_collection.insert_one(prediction_data)
            
            # Pass prediction result to result.html
            return render_template('result.html', prediction_text=message, immunity_index=immunity_index)
        else:
            return render_template("prediction.html")
    else:
        return redirect(url_for('index'))

@app.route("/dashboard")
def dashboard():
    if 'email' in session:
        # Retrieve prediction data from MongoDB
        predictions = list(prediction_collection.find({"email": session['email']}))
        # Convert ObjectId to serializable format
        for prediction in predictions:
            prediction['_id'] = str(prediction['_id'])
        return render_template("d2.html", predictions=predictions)
    else:
        return redirect(url_for('index'))

@app.route("/profile")
def profile():
    if 'email' in session:
        email = session['email']
        user = users_collection.find_one({'email': email})
        if user:
            return render_template("profile.html", users=user)  # Pass user data to the template
    return redirect(url_for('index'))


@app.route('/get_user_details')
def get_user_details():
    # Assuming you have some logic to identify the current user, for example using session data
    # For demonstration, let's assume the user's email is stored in a session variable
    email = session.get('email')

    # Fetch user details from the database based on the email
    users = users_collection.find_one({'email': email})

    # Return user details as JSON
    return jsonify(users)

if __name__ == "__main__":
    app.run(debug=True)
