# Anti Money Laundering Detection and alert generation wesite 
Developed an Anti-Money Laundering (AML) transaction monitoring system featuring real-time fraud detection using machine learning models. Automated the generation of email alerts with detailed reports of suspicious transactions, enabling timely review and response.

## Project Overview
This project is an **Anti-Money Laundering (AML) Transaction Monitoring System** designed to detect suspicious financial activities. It leverages machine learning models for real-time fraud detection and sends automated email alerts with detailed reports of flagged transactions for review.

## Features
- **Real-Time Monitoring**: Detects suspicious transactions based on predefined thresholds.
- **Machine Learning Integration**: Utilizes ML models for fraud detection.
- **Automated Email Alerts**: Sends alerts with a report of flagged transactions.
- **CSV File Export**: Allows exporting of suspicious transactions to CSV format for analysis.



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
