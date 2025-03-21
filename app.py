from flask import Flask, render_template, redirect, url_for, request, flash, send_file
import pandas as pd
import numpy as np
import sqlite3
import os
import io
import joblib
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from send_alert_email import send_alert_email 


app = Flask(__name__)
app.secret_key = 'Saurav@123'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Sample user credentials
users = {'admin': '123456789'}

# File paths (assuming files are in the same directory as this script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'best_gradient_boosting_model.pkl')
ENCODERS_PATH = os.path.join(BASE_DIR, 'label_encoders.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'scaler.pkl')

# Debugging: Print file paths
print(f"Model path: {MODEL_PATH}")
print(f"Encoders path: {ENCODERS_PATH}")
print(f"Scaler path: {SCALER_PATH}")

# Check if files exist
for path in [MODEL_PATH, ENCODERS_PATH, SCALER_PATH]:
    if not os.path.isfile(path):
        print(f"File not found: {path}")

# Load model, encoders, and scaler
try:
    model = joblib.load(MODEL_PATH)
    label_encoders = joblib.load(ENCODERS_PATH)
    scaler = joblib.load(SCALER_PATH)
except FileNotFoundError as e:
    print(f"File not found: {e}")
    raise

# Ensure the upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# To store uploaded data temporarily
uploaded_data = None
predicted_data = None

# Database connection function
def connect_db():
    return sqlite3.connect('aml_database.db')

# Define the base directory and DB path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'aml_database.db')


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username] == password:
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/view-customers')
def view_customers():
    conn = connect_db()
    try:
        # Fetch all records from the customers table
        df = pd.read_sql('SELECT * FROM customers', conn)
        data = df.to_dict(orient='records')
    except Exception as e:
        flash(f'An error occurred while fetching data: {e}', 'danger')
        data = []
    finally:
        conn.close()
    return render_template('view_customers.html', data=data)

@app.route('/analyze-transactions', methods=['GET', 'POST'])
def analyze_transactions():
    global uploaded_data, predicted_data
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Load CSV into DataFrame
            global uploaded_data
            uploaded_data = pd.read_csv(filepath)

            flash('File uploaded successfully!', 'success')
            return redirect(url_for('analyze_transactions'))

    if uploaded_data is not None:
        data_preview = uploaded_data.head(10).to_dict(orient='records')
        return render_template('upload_transactions.html', data=data_preview)
    
    return render_template('upload_transactions.html', data=None)

def preprocess_data(df):
    # List of columns used during model training
    required_columns = ['Sender Account No.', 'Sender Country', 'Receiver Account No.', 'Amount', 'Week']
    
    # Ensure all required columns are present
    for col in required_columns:
        if col not in df.columns:
            df[col] = np.nan  # Add missing columns with NaN values

    # Handle missing columns
    df = df[required_columns]

    # Encode categorical columns
    for column, le in encoders.items():
        if column in df.columns:
            df[column] = le.transform(df[column].astype(str))

    # Scale numerical columns
    numerical_columns = ['Amount']  # Add other numerical columns if necessary
    if all(col in df.columns for col in numerical_columns):
        df[numerical_columns] = scaler.transform(df[numerical_columns])
    
    return df

@app.route('/upload_transactions', methods=['GET', 'POST'])
def upload_transactions():
    data_html = None  # Initialize the variable to store the HTML of the data preview
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return render_template('upload_transactions.html', data=data_html)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return render_template('upload_transactions.html', data=data_html)

        if file:
            # Read the file and display data preview
            data = pd.read_csv(io.StringIO(file.stream.read().decode("UTF8")), sep=",")
            for column in ['Sender Account No.', 'Receiver Account No.']:
                if column in data.columns:
                    data[column] = data[column].astype(str)
            data_html = data.head(10).to_html(classes='table table-bordered', index=False)
            # Save the uploaded data to a session or a temporary location
            data.to_csv('uploaded_transactions.csv', index=False)
        
    return render_template('upload_transactions.html', data=data_html)

def send_alert_email(sender_email, sender_password, receiver_email, subject, body, attachment_path=None):
    # Create a secure SSL context
    context = ssl.create_default_context()

    # Create the email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(body, "html"))  # Use HTML format to support symbols

    # Attach file if provided
    if attachment_path and os.path.isfile(attachment_path):
        try:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(attachment_path)}",
                )
                message.attach(part)
        except Exception as e:
            print(f"Error attaching file: {e}")

    # Send the email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/generate_predictions', methods=['GET', 'POST'])
def generate_predictions():
    predictions_html = None
    download_link = None
    
    if request.method == 'GET':
        try:
            # Load the uploaded transactions data
            data = pd.read_csv('uploaded_transactions.csv')

            # Drop columns not used for prediction
            columns_to_drop = ['Transaction ID']
            data = data.drop(columns=columns_to_drop, errors='ignore')

            # Ensure the remaining columns match those used during model training
            required_columns = ['Sender Account No.', 'Sender Country', 'Receiver Account No.', 'Amount', 'Week']
            for col in required_columns:
                if col not in data.columns:
                    data[col] = np.nan
            data = data[required_columns]

            # Load encoders and scaler
            label_encoders = joblib.load(ENCODERS_PATH)
            scaler = joblib.load(SCALER_PATH)
            
            # Encode categorical variables
            categorical_columns = ['Sender Country']
            for column in categorical_columns:
                if column in data.columns:
                    le = label_encoders.get(column)
                    if le:
                        data[column] = le.transform(data[column].astype(str))

            # Scale numerical features
            numerical_columns = ['Amount']
            if all(col in data.columns for col in numerical_columns):
                data[numerical_columns] = scaler.transform(data[numerical_columns])
            
            # Generate predictions
            X = data.drop(['Label'], axis=1, errors='ignore')
            predictions = model.predict(X)
            data['Prediction'] = predictions

            # Inverse transform the scaled 'Amount' column
            if 'Amount' in data.columns:
                data['Amount'] = scaler.inverse_transform(data[['Amount']])
            
            # Reverse encoding for 'Sender Country'
            if 'Sender Country' in data.columns:
                data['Sender Country'] = label_encoders['Sender Country'].inverse_transform(data['Sender Country'])
            
            # Fix formatting of 'Sender Account No.'
            if 'Sender Account No.' in data.columns:
                data['Sender Account No.'] = data['Sender Account No.'].apply(lambda x: f"{int(x):,}")
            
            # Filter out fraudulent transactions
            fraudulent_data = data[data['Prediction'] == 1]
            
            # Save the predictions to a CSV file
            csv_file_path = 'fraudulent_predictions.csv'
            fraudulent_data.to_csv(csv_file_path, index=False)
            
            # Convert to HTML for display
            predictions_html = fraudulent_data.to_html(classes='table table-bordered', index=False)
            download_link = url_for('download_predictions')
        
        except Exception as e:
            predictions_html = "<p>An error occurred while generating predictions. Please check the logs for more details.</p>"
    
    return render_template('generate_predictions.html', predictions=predictions_html, download_link=download_link)


@app.route('/download_predictions', methods=['GET'])
def download_predictions():
    # Download the fraudulent predictions CSV file
    return send_file('fraudulent_predictions.csv', as_attachment=True)



@app.route('/generate_alert', methods=['POST'])
def generate_alert():
    try:
        # Default sender email and password
        sender_email = "abc123@gmail.com"
        sender_password = "izls eage ipkp frcv"  # Use your App Password for Gmail

        # Get receiver email from the form
        receiver_email = request.form.get('receiver_email')

        # Email subject and body
        subject = "🚨 Urgent: Suspicious Transactions Detected - Immediate Review Required 🚨"
        body = """
        <html>
        <body>
        <p>Dear Financial Security Officer,</p>
        <p><strong>🔍 Important Notice:</strong> Suspicious activities have been detected and require your immediate attention.</p>
        <p><strong>Summary of Alerts:</strong></p>
        <ul>
            <li>💰 <strong>High-Value Transactions:</strong> Transactions exceeding <strong>$10,000</strong> per week have been monitored for potential suspicious activity.</li>
            <li>🌍 <strong>High-Risk Countries:</strong> Alerts have been generated for transactions over <strong>$1,000</strong> from countries classified as high-risk.</li>
        </ul>
        <p><strong>Attachment:</strong></p>
        <ul>
            <li>📄 <strong>File Name:</strong> fraudulent_transactions (2).csv</li>
            <li>📋 <strong>Description:</strong> This file contains details of the flagged transactions for your review.</li>
        </ul>
        <p><strong>Action Required:</strong></p>
        <p>Please review the attached file and take the necessary actions, including investigating the transactions and considering account suspension if warranted.</p>
        <p>For further information or assistance, do not hesitate to contact me directly.</p>
        <p>Thank you for your prompt attention to this matter.</p>
        <p>Best regards,</p>
        <p>AML TEAM<br>
        <strong>Anti-Money Laundering (AML) Specialist</strong><br>
        SecureFinance Solutions<br>
        📧 amlteam@gmail.com<br>
        📞 +918767647450</p>
        </body>
        </html>
        """

        # Ensure the path to the CSV file is correct
        attachment_path = 'fraudulent_predictions.csv'
        
        # Verify file exists
        if not os.path.isfile(attachment_path):
            print(f"Attachment file not found: {attachment_path}")
            flash(f"Attachment file not found: {attachment_path}", "danger")
            return redirect(url_for('generate_predictions'))

        # Call the function to send email
        send_alert_email(sender_email, sender_password, receiver_email, subject, body, attachment_path=attachment_path)
        
        # Show success message after sending email
        flash("Email sent successfully!", "success")
    
    except Exception as e:
        print(f"Error generating alert: {e}")
        flash("An error occurred while generating the alert. Please try again.", "danger")
    
    return redirect(url_for('generate_predictions'))




if __name__ == '__main__':
    app.run(debug=True)
