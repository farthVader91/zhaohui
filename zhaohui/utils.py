import argparse
import csv
import os

from oauth2client import client
from oauth2client import file as oauthFile
from oauth2client import tools

from constants import API_SCOPES, CREDENTIAL_STORE_FILE, API_NAME, API_VERSION


def get_arguments(argv, desc, parents=None):
    parent_parsers = [tools.argparser]
    if parents:
        parent_parsers.extend(parents)
    parser = argparse.ArgumentParser(
      description=desc,
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=parent_parsers)
    return parser.parse_args(argv)


def oAuth():
    argparser = argparse.ArgumentParser(add_help=False)
    argparser.add_argument('profile_id', type=int,
                       help='The ID of the profile to add a placement for')
    
    file = csv.reader(open("/Users/peiyan/Documents/MightyHive/DCM_Trafficking/file2.csv", "rU"))
    for argv in file:
        flags = get_arguments(argv, __doc__, parents=[argparser])
    profileId = argv[0]
        
    client_secrets = os.path.join("/Users/peiyan/Documents/MightyHive/DCM_Trafficking",
                                'client_secret_827029712124-5i2d5vmkeeeqsqs5mnqdpeiotls63j20.apps.googleusercontent.com.json')
    flow = client.flow_from_clientsecrets(
        client_secrets,
        scope=API_SCOPES,
        message=tools.message_if_missing(client_secrets))
    storage = oauthFile.Storage(CREDENTIAL_STORE_FILE)
    credentials = storage.get()
     
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    http = credentials.authorize(http=httplib2.Http())

    return [discovery.build(API_NAME, API_VERSION, http=http),profileId]