# Anti Money Laundering Detection and alert generation wesite 
Developed an Anti-Money Laundering (AML) transaction monitoring system featuring real-time fraud detection using machine learning models. Automated the generation of email alerts with detailed reports of suspicious transactions, enabling timely review and response.

## Project Overview
This project is an **Anti-Money Laundering (AML) Transaction Monitoring System** designed to detect suspicious financial activities. It leverages machine learning models for real-time fraud detection and sends automated email alerts with detailed reports of flagged transactions for review.

## Features
- **Real-Time Monitoring**: Detects suspicious transactions based on predefined thresholds.
- **Machine Learning Integration**: Utilizes ML models for fraud detection.
- **Automated Email Alerts**: Sends alerts with a report of flagged transactions.
- **CSV File Export**: Allows exporting of suspicious transactions to CSV format for analysis.
  
## Video Demo
[![Watch the demo](https://img.youtube.com/vi/2hC-rVhY9ls/0.jpg)](https://youtu.be/2hC-rVhY9ls)

Click on the image above to watch the video demonstration.


## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/SauravBedse223/Anti-Money-Laundering-Detection-and-alert-generation.git
    cd Anti-Money-Laundering-Detection-and-alert-generation
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up your email credentials:
    - In the `app.py` file, update the `sender_email` and `sender_password` with your email and app-specific password for sending alerts.

4. Run the application:
    ```bash
    python app.py
    ```

5. Open the application in your browser at `http://127.0.0.1:5000`.

## Project Structure

```bash
aml-transaction-monitoring/
│
├── static/
│   └── style.css           # Stylesheet for the web pages
├── templates/
│   ├── login.html          # Login page
│   ├── generate_predictions.html # Results and alert page
│   └── dashboard.html      # Dashboard page
├── app.py                  # Main Flask app
├── fraudulent_predictions.csv  # Example output of flagged transactions
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── demo.mp4                # Video of the working project (optional)
