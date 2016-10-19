from flask import Flask, request
from flask import render_template, redirect

from forms import UploadCampaignForm

from utils import create_campaign, store_csv, make_campaign_entry

app = Flask(__name__)
app.secret_key = 'some-arbitary-secret-key'


@app.route('/', methods=['GET', 'POST']) 
def upload_form():
    form = UploadCampaignForm()
    if form.validate_on_submit():
        print 'creating campaign for given csv...'
        status_flag = True
        try:
            status_flag, failed_ads = create_campaign(form.profile_id.data, form.csv.data) 
            form.csv.data.seek(0, 0)
        except Exception as err:
            print 'error creating campaign'
            print err
            status_flag = False
            failed_ads = set()
        # store the csv file
        try: 
            blob = store_csv(form.csv.data)
        except Exception:
            return redirect('/fail')
        
        # make/update entry
        make_campaign_entry(
            form.profile_id.data,
            form.email.data,
            blob,
            status_flag,
            list(failed_ads),
          
        )
        
        return redirect('/success')
    return render_template('upload_campaign.html', form=form)


@app.route('/success')
def success():
    return render_template('2view.html')


@app.route('/fail')
def fail():
    return render_template('fail.html')


@app.route('/loading')
def loading():
    return render_template('loading_page.html')

if __name__ == '__main__':
    app.run(debug=True)