import os

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import TextField, SelectField, validators
from zhaohui.constants import profile_info



def is_csv(message=u'Only csv files are allowed'):
    def _is_csv(form, field):
        _, ext = os.path.splitext(field.data.filename)
        if ext.lower() != '.csv':
            raise validators.ValidationError(message)
    return _is_csv


class UploadCampaignForm(FlaskForm):

    """Take inputs from user:
        1.select the DCM seat they want to push trafficking to.
        2.input a valid email address
        3.upload a valid csv file
    """
    profile_id = SelectField(
        "",
        choices=profile_info,
        validators=[validators.required()],
        coerce = int
    )
    email = TextField(
        'Email',
        validators=[validators.Email(), validators.required()]
    )
    csv = FileField(
        'Campaign File',
        validators=[validators.required(), is_csv()]
    )