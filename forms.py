import os

import pandas as pd

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import TextField, SelectField, validators
from zhaohui.constants import profile_info



def validate_csv(message=u'Only csv files are allowed'):
    def validate_columns(df):
        req_columns = set([
            'Advertiser_id',
            'campaign_name',
            'startdate',
            'enddate',
            'default_url_name',
            'default_url',
            'placement_name',
            'compatibility',
            'directorySIte_ID',
            'width',
            'height',
            'ad_name',
            'ad_type',
            'Ad_start_date',
            'Ad_end_date',
            'rotation_weight',
            'rotation_type',
            'creative_name',
            'custom_url',
        ])
        existing_columns = set(df.columns)
        missing_cols = req_columns - existing_columns
        if missing_cols:
            message = 'Following headers are missing:\n%s' % ('\n'.join(missing_cols))
            raise validators.ValidationError(message)
    def validate_dates(df):
        pass
    def validate_urls(df):
        pass
    def _validate_csv(form, field):
        _, ext = os.path.splitext(field.data.filename)
        # ensure extension is of type *.csv
        if ext.lower() != '.csv':
            raise validators.ValidationError(message)
        # load the file obj into a pd dataframe
        df = pd.read_csv(field.data)
        # ensure all required columns exist
        validate_columns(df)
        # ensure all start dates are gte today
        validate_dates(df)
        # ensure all urls utilise https/http schemes
        validate_urls(df)
    return _validate_csv


class UploadCampaignForm(FlaskForm):

    """Take inputs from user:
        1.select the DCM seat they want to push trafficking to.
        2.input a valid email address
        3.upload a valid csv file
    """
    profile_id = SelectField(
        "",
        choices=[[1, 'A']],
        validators=[validators.required()],
        coerce = int
    )
    email = TextField(
        'Email',
        validators=[validators.Email(), validators.required()]
    )
    csv = FileField(
        'Campaign File',
        validators=[validators.required(), validate_csv()]
    )