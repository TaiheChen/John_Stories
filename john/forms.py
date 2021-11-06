from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextField, TextAreaField
from wtforms.validators import InputRequired, Email, EqualTo

# Form for the submit a new story
class EditStoryForm(FlaskForm):
    title = StringField("Story's title", validators=[InputRequired()])
    content = TextAreaField("Story's content", validators=[InputRequired()])
    submit = SubmitField("Submit Story")
