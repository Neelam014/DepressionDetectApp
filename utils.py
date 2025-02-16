from datetime import datetime
import pdfkit
from flask import render_template

def format_datetime(dt):
    """Format datetime object to string."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_depression_level(score):
    """Determine depression level based on PHQ-9 score."""
    if score <= 4:
        return 'Minimal'
    elif score <= 9:
        return 'Mild'
    elif score <= 14:
        return 'Moderate'
    elif score <= 19:
        return 'Moderately Severe'
    else:
        return 'Severe'

def get_anxiety_level(score):
    """Determine anxiety level based on GAD-7 score."""
    if score <= 4:
        return 'Minimal'
    elif score <= 9:
        return 'Mild'
    elif score <= 14:
        return 'Moderate'
    else:
        return 'Severe'

def get_recommendations(assessment):
    """Get recommendations based on assessment scores."""
    recommendations = []
    
    # Depression recommendations
    if assessment.level in ['Moderately Severe', 'Severe']:
        recommendations.extend([
            'Seek professional help immediately',
            'Contact National Crisis Helpline: 988',
            'Schedule an appointment with a mental health professional'
        ])
    elif assessment.level == 'Moderate':
        recommendations.extend([
            'Consider speaking with a mental health professional',
            'Practice daily mindfulness exercises',
            'Maintain a regular sleep schedule'
        ])
    else:
        recommendations.extend([
            'Continue monitoring your mental health',
            'Practice self-care routines',
            'Stay connected with friends and family'
        ])
    
    # Anxiety recommendations
    if assessment.anxiety_level in ['Moderate', 'Severe']:
        recommendations.extend([
            'Try breathing exercises when feeling anxious',
            'Consider anxiety management techniques',
            'Limit caffeine and alcohol intake'
        ])
    
    # Lifestyle recommendations
    if assessment.sleep_hours < 6:
        recommendations.append('Work on improving sleep duration (aim for 7-9 hours)')
    if assessment.exercise_minutes < 30:
        recommendations.append('Try to increase physical activity (aim for 30+ minutes daily)')
    
    return recommendations

def generate_pdf_report(assessment, user):
    """Generate PDF report from assessment data."""
    rendered = render_template('report_pdf.html',
                             assessment=assessment,
                             user=user,
                             recommendations=get_recommendations(assessment))
    
    pdf_options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
    }
    
    # Generate PDF using pdfkit
    pdf = pdfkit.from_string(rendered, False, options=pdf_options)
    return pdf
