import argparse
import csv
import os
import httplib2

from googleapiclient import discovery
from oauth2client import client
from oauth2client import file as oauthFile
from oauth2client import tools

from constants import API_SCOPES, API_NAME, API_VERSION
from constants import ARGS_FILE, CLIENT_SECRET_FILE, CREDENTIAL_STORE_FILE


def get_arguments(argv, desc, parents=None):
    parent_parsers = [tools.argparser]
    if parents:
        parent_parsers.extend(parents)
    parser = argparse.ArgumentParser(
      description=desc,
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=parent_parsers)
    return parser.parse_args(argv)


def get_service_and_profile_id():
    argparser = argparse.ArgumentParser(add_help=False)
    argparser.add_argument('profile_id', type=int,
                       help='The ID of the profile to add a placement for')

    with open(ARGS_FILE, 'rU') as argsf:
        reader = csv.reader(argsf)
        for argv in reader:
            flags = get_arguments(argv, __doc__, parents=[argparser])
        profileId = argv[0]

    flow = client.flow_from_clientsecrets(
        CLIENT_SECRET_FILE,
        scope=API_SCOPES,
        message=tools.message_if_missing(CLIENT_SECRET_FILE))
    storage = oauthFile.Storage(CREDENTIAL_STORE_FILE)
    credentials = storage.get()
     
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    http = credentials.authorize(http=httplib2.Http())

    return [discovery.build(API_NAME, API_VERSION, http=http),profileId]