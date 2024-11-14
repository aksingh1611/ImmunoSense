from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np

app = Flask(__name__)
model = pickle.load(open('decision_tree_regression_model.pkl', 'rb'))
scaler = pickle.load(open('scaler.pickle', 'rb'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    int_features = [int(x) for x in request.form.values()]
    print("intial values -->", int_features)
    pre_final_features = [np.array(int_features)]
    final_features = scaler.transform(pre_final_features)
    print("scaled values -->", final_features)
    
    # Use the model to predict the immunity index
    pred = model.predict(final_features)
    immunity_index = pred[0]
    
    if immunity_index > 25:
        message = "Minimum Immunity: 10, Maximum Immunity: 30\nYour immunity index is Good! \nHealthy Diet, Regular Exercise, Adequate Sleep, Stress Management, Hydration \nAvoid Smoking and Limit Alcohol \nRegular Health Check-ups, Stay Informed"
    elif 16 <= immunity_index <= 25:
        message = "Minimum Immunity: 10, Maximum Immunity: 30\nYour immunity index is moderate! \nBalanced Diet, Hydration, Avoid Smoking and Limit Alcohol, Regular Exercise, \nAdequate Sleep, Stress Management \nImmune-Boosting Foods and Supplements, Good Hygiene Practices \nRegular Health Check-ups, Stay Informed"
    else:
        message = "Minimum Immunity: 10, Maximum Immunity: 30\nYour immunity index is poor! \nNutritious Diet, Supplements, Regular Exercise, Quit Smoking, Stress Management, \nLimit Alcohol, Good Hygiene Practices, Adequate Sleep, \nAvoid Exposure to Illness, Medical Check-up, Stay Informed"
    return render_template('index.html', prediction_text=message)

        
if __name__ == "__main__":
    app.run(debug=True)