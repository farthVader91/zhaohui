from flask import Flask
from flask import render_template, redirect

from forms import UploadCampaignForm


app = Flask(__name__)
app.secret_key = 'some-arbitary-secret-key'

@app.route('/', methods=['GET', 'POST'])
def upload_form():
    form = UploadCampaignForm()
    if form.validate_on_submit():
        return redirect('/success')
    return render_template('upload_campaign.html', form=form)


@app.route('/success')
def success():
    return render_template('2view.html')

if __name__ == '__main__':
    app.run(debug=True)