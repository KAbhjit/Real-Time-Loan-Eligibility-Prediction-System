# app.py
from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Load models and scaler
rf_model = joblib.load('random_forest_model.pkl')
xgb_model = joblib.load('xgboost_model.pkl')
scaler = joblib.load('scaler.pkl')

app = Flask(__name__)

# Define features for input
required_features = [
    'AnnualIncome', 'CreditScore', 'Experience', 'LengthOfCreditHistory',
    'EducationLevel', 'UtilityBillsPaymentHistory', 'MonthlyLoanPayment', 
    'NetWorth', 'EmploymentStatus', 'SavingsAccountBalance', 'BaseInterestRate',
    'CheckingAccountBalance', 'LoanAmount', 'InterestRate', 'BankruptcyHistory',
    'PaymentHistory', 'NumberOfCreditInquiries', 'LoanDuration', 'Age', 'RiskScore',
    'NumberOfOpenCreditLines', 'PreviousLoanDefaults', 'TotalDebtToIncomeRatio',
    'CreditCardUtilizationRate', 'NumberOfDependents', 'TotalLiabilities', 
    'MonthlyDebtPayments'
]

# Function to preprocess input data
def preprocess_input(data):
    df = pd.DataFrame([data])

    # Ensure all required features are included and in the correct order
    for feature in required_features:
        if feature not in df.columns:
            df[feature] = None

    # Convert categorical variables if necessary
    categorical_features = ['EducationLevel', 'BankruptcyHistory', 'PaymentHistory', 'EmploymentStatus']
    df = pd.get_dummies(df, columns=categorical_features)

    # Align columns with the model's expected input
    df = df.reindex(columns=required_features, fill_value=0)
    
    # Scale the data
    df_scaled = scaler.transform(df)
    return df_scaled

# Route to render HTML page
@app.route('/')
def home():
    return render_template('index.html')

# Eligibility Prediction Endpoint
@app.route('/predict_eligibility', methods=['POST'])
def predict_eligibility():
    data = request.json
    try:
        processed_data = preprocess_input(data)
        prediction = rf_model.predict(processed_data)
        return jsonify({'eligibility': int(prediction[0])})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Loan Recommendation Endpoint
@app.route('/recommend_loan', methods=['POST'])
def recommend_loan():
    data = request.json
    try:
        processed_data = preprocess_input(data)
        
        # Get general recommendation from the model
        is_recommended = xgb_model.predict(processed_data)[0]
        
        # Define specific loan recommendations
        if is_recommended:
            annual_income = data.get("AnnualIncome", 0)
            age = data.get("Age", 0)
            credit_score = data.get("CreditScore", 0)
            education_level = data.get("EducationLevel", 0)
            loan_amount = data.get("LoanAmount", 0)

            # Check specific loan type conditions
            if annual_income > 70000 and credit_score > 700:
                loan_type = "Home Loan"
            elif age <= 30 and education_level >= 2 and loan_amount < 20000:
                loan_type = "Student Loan"
            elif annual_income > 40000 and credit_score > 600:
                loan_type = "Personal Loan"
            else:
                loan_type = "Not eligible for specific loan types"
                
            return jsonify({
                'recommendation': f"Loan Recommended: {loan_type}"
            })
        else:
            return jsonify({
                'recommendation': "Loan Not Recommended"
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
