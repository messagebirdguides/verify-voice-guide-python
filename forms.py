from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.fields.html5 import TelField #telephone number field

#Defines fields in forms. Includes definitions of validators.

class SubmitPhoneNumber(FlaskForm):
    number = TelField('Phone number')
    submit = SubmitField('Send code')

class EnterCode(FlaskForm):
    verify_id = HiddenField('ID')
    token = StringField('Enter your verification code:')
    submit = SubmitField('Check code')
