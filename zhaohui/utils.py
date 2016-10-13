import argparse
import csv
import os
import httplib2

from oauth2client.contrib import gce
from googleapiclient import discovery
from oauth2client import client
from oauth2client import file as oauthFile
from oauth2client import tools

from constants import API_SCOPES, API_NAME, API_VERSION
from constants import ARGS_FILE, CLIENT_SECRET_FILE, CREDENTIAL_STORE_FILE
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
import webbrowser



def get_service_and_profile_id():
    # profileId = form.profile_id.data
    # print profileId
    

    flow = client.flow_from_clientsecrets(
        CLIENT_SECRET_FILE,
        scope=API_SCOPES,
        redirect_uri = "http://localhost:5000"
        )
    storage = oauthFile.Storage(CREDENTIAL_STORE_FILE)
    credentials = storage.get()
     
    if credentials is None or credentials.invalid:
        auth_uri = flow.step1_get_authorize_url(redirect_uri="http://localhost")
        webbrowser.open(auth_uri)
        code = raw_input('Enter verification code: ').strip()
        credentials = flow.step2_exchange(code)
        storage = Storage(CREDENTIAL_STORE_FILE)
        storage.put(credentials)

    http = credentials.authorize(http=httplib2.Http())

    return discovery.build(API_NAME, API_VERSION, http=http)