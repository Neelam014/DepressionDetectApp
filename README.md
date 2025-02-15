# VirtuWellness Hub

A comprehensive mental health assessment and monitoring platform that uses machine learning to provide personalized insights and recommendations.

## Project Structure

```
VirtuWellness Hub/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── models.py           # Database models
├── utils.py            # Helper functions
├── ml_models.py        # Machine learning models and predictions
├── init_db.py          # Database initialization script
├── requirements.txt    # Python dependencies
├── static/            
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript files
│   └── images/        # Image assets
├── templates/          # HTML templates
│   ├── base.html      # Base template
│   ├── index.html     # Landing page
│   ├── login.html     # Login page
│   ├── signup.html    # Signup page
│   ├── dashboard.html # User dashboard
│   └── ...           # Other templates
├── models/            # Trained ML models
│   ├── encoder.pkl
│   ├── lstm_model.h5
│   ├── scaler.pkl
│   └── svm_model.pkl
└── instance/          # Instance-specific files
    └── virtuwellness.db  # SQLite database
```

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python init_db.py
   ```

4. Run the application:
   ```bash
   python -m flask run
   ```

## Features

- Mental health assessment using PHQ-9 (depression) and GAD-7 (anxiety) questionnaires
- Machine learning predictions using SVM and LSTM models
- Progress tracking and reporting
- Mindful activities recommendations
- PDF report generation

## Dependencies

- Flask
- Flask-SQLAlchemy
- Flask-Login
- TensorFlow
- Scikit-learn
- PDFKit (requires wkhtmltopdf)

## Notes

- The application is currently designed for female users only
- Ensure wkhtmltopdf is installed for PDF generation
- ML models should be placed in the models/ directory
