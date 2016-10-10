from flask.ext.wtf import Form

from wtforms import FileField, validators

class UploadCampaignForm(Form):
    csv = FileField('Select File')