from flask import Flask, request
from flask import render_template, redirect

from flask_login import LoginManager

from forms import UploadCampaignForm
from utils import create_campaign, store_csv, make_campaign_entry

app = Flask(__name__)
app.secret_key = 'some-arbitary-secret-key'

login_manager = LoginManager()
login_manager.init_app(app)

from functools import wraps
from flask import request, Response


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/', methods=['GET', 'POST']) 
@requires_auth
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