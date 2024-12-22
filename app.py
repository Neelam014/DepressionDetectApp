
from flask import Flask, render_template, request, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
Bootstrap(app)

questions = [
    "I have felt down, depressed, or hopeless.",
    "I have felt little interest or pleasure in doing things.",
    "I have had trouble sleeping or sleeping too much.",
    "I have felt tired or had little energy.",
    "I have had poor appetite or eaten too much.",
    "I have felt bad about myself – or that I am a failure or have let people down.",
    "I have had trouble concentrating on things, such as reading the newspaper or watching television.",
    "I have moved or spoken so slowly that other people could notice.",
    "I have thought that I would be better off dead or of hurting myself.",
    "I have not felt like myself at all."
]

depression_levels = {
    range(1, 6): "Minimal or No Depression",
    range(6, 11): "Mild Depression",
    range(11, 16): "Moderate Depression",
    range(16, 21): "Moderately Severe Depression",
    range(21, 31): "Severe Depression"
}

intervention_suggestions = {
    "Minimal or No Depression": "You are doing great! Maintain your positive practices.",
    "Mild Depression": "Consider engaging in mindfulness exercises and seeking support from loved ones.",
    "Moderate Depression": "Seeking professional help from a therapist or counselor is recommended.",
    "Moderately Severe Depression": "Consult a mental health professional for further evaluation and treatment.",
    "Severe Depression": "Immediate professional help is crucial, consider seeking medication and therapy."
}

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")

class QuestionForm(FlaskForm):
    response = SelectField("Response", choices=[("1", "Strongly Disagree"), ("2", "Disagree"), ("3", "Neutral"), ("4", "Agree"), ("5", "Strongly Agree")], validators=[DataRequired()])
    submit = SubmitField("Next")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        return redirect(url_for("home"))
    return render_template("signup.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for("assessment", question_index=0))
    return render_template("login.html", form=form)

@app.route("/assessment/<int:question_index>", methods=["GET", "POST"])
def assessment(question_index):
    form = QuestionForm()
    if question_index == 0:
        session["responses"] = []

    if form.validate_on_submit():
        session["responses"].append(int(form.response.data))
        if question_index + 1 < len(questions):
            return redirect(url_for("assessment", question_index=question_index + 1))
        else:
            return redirect(url_for("results"))

    return render_template("assessment.html", question=questions[question_index], form=form, question_index=question_index, total_questions=len(questions))

@app.route("/results")
def results():
    responses = session.get("responses", [])
    if not responses:
        return redirect(url_for("home"))

    score = sum(responses)
    level = next((v for k, v in depression_levels.items() if score in k), "Unknown")
    suggestion = intervention_suggestions.get(level, "No suggestion available.")

    return render_template("results.html", score=score, level=level, suggestion=suggestion)

if __name__ == "__main__":
    app.run(debug=True)
