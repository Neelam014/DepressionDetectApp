from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import json
import matplotlib.pyplot as plt
import io
import pdfkit
from urllib.parse import urlparse
import base64

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wellness.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), nullable=True)
    family_history = db.Column(db.Text, nullable=True)
    assessments = db.relationship('Assessment', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Assessment Model
class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    phq9_score = db.Column(db.Float)
    depression_severity = db.Column(db.String(20))
    svm_confidence = db.Column(db.Float)
    lstm_confidence = db.Column(db.Float)
    sentiment = db.Column(db.String(10))
    age = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), nullable=True)
    family_history = db.Column(db.Boolean, nullable=True)
    recommendations = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Redirect to dashboard if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        gender = request.form.get('gender')

        # Validate required fields
        if not all([name, email, password, gender]):
            flash('All fields are required', 'danger')
            return redirect(url_for('signup'))

        # Validate password length
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return redirect(url_for('signup'))

        # Validate gender restriction
        if gender == 'male':
            flash('This application is currently only available for female users', 'warning')
            return redirect(url_for('signup'))

        try:
            # Check if email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('This email is already registered. Please login instead.', 'warning')
                return redirect(url_for('login'))

            # Create new user
            new_user = User(
                name=name,
                email=email,
                gender=gender
            )
            new_user.set_password(password)

            # Add user to database
            db.session.add(new_user)
            db.session.commit()

            # Log the user in
            login_user(new_user)
            flash('Account created successfully! Welcome!', 'success')
            return redirect(url_for('dashboard'))

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error during signup: {str(e)}")
            flash('An error occurred during signup. Please try again.', 'danger')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect to dashboard if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False) == 'on'

        if not email or not password:
            flash('Please provide both email and password', 'danger')
            return redirect(url_for('login'))

        try:
            # Find user by email
            user = User.query.filter_by(email=email).first()

            # Check if user exists and password is correct
            if user and user.check_password(password):
                login_user(user, remember=remember)
                flash('Logged in successfully!', 'success')

                # Get the next page from args or default to dashboard
                next_page = request.args.get('next')
                if not next_page or urlparse(next_page).netloc != '':
                    next_page = url_for('dashboard')
                return redirect(next_page)
            else:
                flash('Invalid email or password', 'danger')
                return redirect(url_for('login'))

        except Exception as e:
            app.logger.error(f"Error during login: {str(e)}")
            flash('An error occurred during login. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    if request.method == 'POST':
        age = request.form.get('age')
        status = request.form.get('status')
        family_history = request.form.get('family_history')

        if not all([age, status, family_history]):
            flash('All fields are required', 'danger')
            return redirect(url_for('onboarding'))

        # Validate status
        valid_statuses = ['Housewife', 'Working Women', 'Student']
        if status not in valid_statuses:
            flash('Invalid status selected', 'danger')
            return redirect(url_for('onboarding'))

        try:
            age = int(age)
            if not (18 <= age <= 100):
                flash('Age must be between 18 and 100', 'danger')
                return redirect(url_for('onboarding'))
        except ValueError:
            flash('Invalid age', 'danger')
            return redirect(url_for('onboarding'))

        current_user.age = age
        current_user.status = status
        current_user.family_history = family_history
        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('onboarding.html')

@app.route('/assessment', methods=['GET', 'POST'])
@login_required
def assessment():
    if request.method == 'POST':
        # Get personal information
        age = request.form.get('age')
        status = request.form.get('status')
        family_history = request.form.get('family_history') == 'true'
        
        # Calculate PHQ-9 score
        phq9_score = sum(int(request.form.get(f'q{i}', 0)) for i in range(1, 10))
        
        # Get written response
        written_response = request.form.get('written_response', '')
        
        # Get initial depression severity from SVM model
        initial_severity = get_depression_severity(phq9_score)
        svm_confidence = calculate_svm_confidence(phq9_score)
        
        # Analyze sentiment using LSTM
        sentiment, lstm_confidence = analyze_sentiment(written_response)
        
        # Adjust severity based on sentiment
        final_severity = adjust_severity_by_sentiment(initial_severity, sentiment)
        
        # Generate recommendations based on status and severity
        recommendations = generate_recommendations(final_severity, status, age)
        
        # Create assessment record
        assessment = Assessment(
            user_id=current_user.id,
            phq9_score=phq9_score,
            depression_severity=final_severity,
            svm_confidence=svm_confidence,
            lstm_confidence=lstm_confidence,
            sentiment=sentiment,
            age=age,
            status=status,
            family_history=family_history,
            recommendations=recommendations
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        return redirect(url_for('results', assessment_id=assessment.id))
    
    return render_template('assessment.html')

@app.route('/submit_assessment', methods=['POST'])
@login_required
def submit_assessment():
    try:
        # Get form data
        answers = []
        raw_total_score = 0
        for i in range(1, 10):  # PHQ-9 has 9 questions
            score = int(request.form.get(f'q{i}', 0))
            if score < 0 or score > 3:  # Each question score must be 0-3
                flash('Invalid score detected. Scores must be between 0 and 3.', 'danger')
                return redirect(url_for('assessment'))
            raw_total_score += score
            answers.append(score)

        # Normalize the score to 0-10 range
        total_score = round((raw_total_score / 27) * 10, 1)  # Convert to 0-10 scale with one decimal

        # Get additional information
        age = request.form.get('age')
        status = request.form.get('status')
        family_history = request.form.get('family_history') == 'yes'

        # Get depression severity
        severity = get_depression_severity(total_score)
        
        # Get recommendations based on severity
        recommendations = get_recommendations(severity)

        # Create new assessment
        assessment = Assessment(
            user_id=current_user.id,
            phq9_score=total_score,
            depression_severity=severity,
            recommendations=recommendations,
            age=age,
            status=status,
            family_history=family_history
        )

        db.session.add(assessment)
        db.session.commit()

        flash('Assessment submitted successfully!', 'success')
        return redirect(url_for('results'))

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error submitting assessment: {str(e)}")
        flash('An error occurred while submitting the assessment. Please try again.', 'danger')
        return redirect(url_for('assessment'))

@app.route('/results/<int:assessment_id>')
@login_required
def results(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)
    if assessment.user_id != current_user.id:
        return redirect(url_for('dashboard'))
    return render_template('results.html', assessment=assessment)

@app.route('/dashboard')
@login_required
def dashboard():
    assessments = Assessment.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', assessments=assessments)

@app.route('/reports')
@login_required
def reports():
    # Get user's assessments ordered by date
    assessments = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.date).all()
    
    if not assessments:
        flash('No assessment data available yet.', 'info')
        return render_template('reports.html', has_data=False)

    # Prepare data for the graph
    dates = []
    scores = []
    severities = []
    
    for assessment in assessments:
        dates.append(assessment.date.strftime('%Y-%m-%d'))
        scores.append(assessment.phq9_score)
        severities.append(assessment.depression_severity)

    # Create the graph
    plt.figure(figsize=(10, 6))
    plt.plot(dates, scores, marker='o', linestyle='-', linewidth=2, markersize=8)
    
    # Customize the graph
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.title('Depression Score Progress', fontsize=14, pad=20)
    plt.xlabel('Assessment Date', fontsize=12)
    plt.ylabel('Depression Score (0-10)', fontsize=12)
    
    # Set y-axis range to 0-10
    plt.ylim(0, 10)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Add score labels on points
    for i, score in enumerate(scores):
        plt.annotate(f'{score:.1f}', (i, score), textcoords="offset points", xytext=(0,10), ha='center')

    # Color points based on severity
    severity_colors = {
        'Mild': 'green',
        'Moderate': 'orange',
        'Severe': 'red'
    }
    
    for i, (severity, score) in enumerate(zip(severities, scores)):
        plt.plot(i, score, 'o', color=severity_colors.get(severity, 'blue'), markersize=10)

    # Add horizontal lines for severity thresholds
    plt.axhline(y=3, color='lightgreen', linestyle='--', alpha=0.5)
    plt.axhline(y=7, color='orange', linestyle='--', alpha=0.5)

    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', label='Mild (0-3)', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', label='Moderate (4-7)', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', label='Severe (8-10)', markersize=10)
    ]
    plt.legend(handles=legend_elements, title='Depression Severity', loc='center left', bbox_to_anchor=(1, 0.5))

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Save plot to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    
    # Convert plot to base64 string
    plot_url = base64.b64encode(buf.getvalue()).decode('utf8')

    return render_template('reports.html', 
                         assessments=assessments,
                         plot_url=plot_url,
                         has_data=True)

def calculate_svm_confidence(phq9_score):
    """Calculate SVM model confidence based on PHQ-9 score."""
    if phq9_score <= 3:
        return 0.90  # Confident for mild depression
    elif phq9_score <= 7:
        return 0.85  # Moderate confidence for moderate depression
    else:
        return 0.80  # Lower confidence for severe cases

def analyze_sentiment(text):
    """Analyze sentiment of written response using LSTM model."""
    # This is a simplified example - in practice, you'd use your trained LSTM model
    # Here we're using basic keyword matching for demonstration
    negative_words = ['sad', 'depressed', 'hopeless', 'worthless', 'tired', 'suicide', 'death']
    positive_words = ['hope', 'better', 'good', 'happy', 'positive', 'improving']
    
    text = text.lower()
    neg_count = sum(1 for word in negative_words if word in text)
    pos_count = sum(1 for word in positive_words if word in text)
    
    total_words = len(text.split())
    if total_words == 0:
        return 'Neutral', 0.5
    
    if neg_count > pos_count:
        confidence = min(0.9, 0.5 + (neg_count - pos_count) / total_words)
        return 'Negative', confidence
    elif pos_count > neg_count:
        confidence = min(0.9, 0.5 + (pos_count - neg_count) / total_words)
        return 'Positive', confidence
    else:
        return 'Neutral', 0.7

def adjust_severity_by_sentiment(severity, sentiment):
    """Adjust depression severity based on sentiment analysis."""
    severity_levels = ['Minimal', 'Mild', 'Moderate', 'Moderately Severe', 'Severe']
    
    if sentiment == 'Negative':
        current_index = severity_levels.index(severity)
        if current_index < len(severity_levels) - 1:
            return severity_levels[current_index + 1]
    
    return severity

def generate_recommendations(severity, status, age):
    """Generate personalized recommendations based on severity and status."""
    base_recommendations = """
    <h5 class="mb-3">General Recommendations:</h5>
    <ul>
        <li>Practice daily mindfulness and meditation</li>
        <li>Maintain a regular sleep schedule</li>
        <li>Exercise for at least 30 minutes daily</li>
        <li>Stay connected with friends and family</li>
    """
    
    # Add status-specific recommendations
    if status == 'student':
        base_recommendations += """
        <h5 class="mt-4 mb-3">Student-Specific Recommendations:</h5>
        <ul>
            <li>Balance study time with breaks and relaxation</li>
            <li>Join study groups or clubs to maintain social connections</li>
            <li>Practice stress-management techniques during exam periods</li>
            <li>Seek help from school counseling services if available</li>
        </ul>
        """
    elif status == 'working_women':
        base_recommendations += """
        <h5 class="mt-4 mb-3">Work-Life Balance Recommendations:</h5>
        <ul>
            <li>Set clear boundaries between work and personal time</li>
            <li>Take regular breaks during work hours</li>
            <li>Practice stress-relief exercises during lunch breaks</li>
            <li>Consider flexible work arrangements if needed</li>
        </ul>
        """
    elif status == 'housewife':
        base_recommendations += """
        <h5 class="mt-4 mb-3">Self-Care Recommendations:</h5>
        <ul>
            <li>Schedule regular "me-time" for personal activities</li>
            <li>Join community groups or classes</li>
            <li>Delegate household tasks when possible</li>
            <li>Maintain a hobby or personal interest</li>
        </ul>
        """
    
    # Add severity-specific recommendations
    if severity in ['Moderately Severe', 'Severe']:
        base_recommendations += """
        <h5 class="mt-4 mb-3 text-danger">Important Health Recommendations:</h5>
        <ul>
            <li class="text-danger"><strong>Schedule an appointment with a mental health professional</strong></li>
            <li>Call the National Suicide Prevention Lifeline (988) if you have thoughts of self-harm</li>
            <li>Consider joining a support group</li>
        </ul>
        """
    
    return base_recommendations

def get_depression_severity(score):
    if score <= 3:
        return "Mild"
    elif score <= 7:
        return "Moderate"
    else:
        return "Severe"

def get_recommendations(severity):
    recommendations = {
        "Mild": "Your symptoms suggest mild depression. Consider practicing self-care techniques and talking to friends or family about your feelings. Regular exercise and mindfulness can be helpful.",
        "Moderate": "Your symptoms indicate moderate depression. It's recommended to schedule a consultation with a mental health professional. Regular counseling and lifestyle changes may be beneficial.",
        "Severe": "Your symptoms suggest severe depression. Please seek professional help as soon as possible. A mental health specialist can help develop an appropriate treatment plan."
    }
    return recommendations.get(severity, "Please consult with a mental health professional for personalized advice.")

@app.route('/api/assessment_history')
@login_required
def assessment_history():
    assessments = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.date).all()
    history = [{
        'date': assessment.date.strftime('%Y-%m-%d'),
        'score': assessment.phq9_score,
        'depression_severity': assessment.depression_severity
    } for assessment in assessments]
    return jsonify(history)

@app.route('/mindful_activities')
@login_required
def mindful_activities():
    return render_template('mindful_activities.html')

@app.route('/download_report')
@login_required
def download_report():
    try:
        # Get user's assessments
        assessments = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.date.desc()).all()
        
        if not assessments:
            flash('No assessment data available to generate report.', 'warning')
            return redirect(url_for('reports'))
            
        # Prepare data for the report
        assessment_data = []
        dates = []
        scores = []
        
        for assessment in assessments:
            dates.append(assessment.date.strftime('%Y-%m-%d'))
            scores.append(assessment.phq9_score)
            assessment_data.append({
                'date': assessment.date.strftime('%Y-%m-%d'),
                'score': assessment.phq9_score,
                'severity': assessment.depression_severity,
                'recommendations': assessment.recommendations
            })
        
        # Create a PDF using a template
        html_content = render_template(
            'report_template.html',
            user=current_user,
            assessments=assessment_data,
            dates=dates,
            scores=scores,
            latest=assessments[0] if assessments else None
        )
        
        # Generate PDF
        pdf = pdfkit.from_string(html_content, False)
        
        # Create response
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=depression_assessment_report_{datetime.now().strftime("%Y%m%d")}.pdf'
        
        return response
        
    except Exception as e:
        flash('Error generating report. Please try again.', 'danger')
        return redirect(url_for('reports'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)