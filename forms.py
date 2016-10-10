import os

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import TextField, SelectField, validators


def is_csv(message=u'Only csv files are allowed'):
    def _is_csv(form, field):
        _, ext = os.path.splitext(field.data.filename)
        if ext.lower() != '.csv':
            raise validators.ValidationError(message)
    return _is_csv


class UploadCampaignForm(FlaskForm):
    profile_id = SelectField(
        'DCM Seat',
        choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')],
        validators=[validators.required()]
    )
    email = TextField(
        'Email',
        validators=[validators.Email(), validators.required()]
    )
    csv = FileField(
        'Campaign File',
        validators=[validators.required(), is_csv()]
    )
