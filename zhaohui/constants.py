import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_ROOT = '/Users/peiyan/Documents/MightyHive/DCM_Trafficking/'

API_NAME = 'dfareporting'   
API_VERSION = 'v2.6'
API_SCOPES = ['https://www.googleapis.com/auth/dfareporting',
              'https://www.googleapis.com/auth/dfatrafficking']

# Filename used for the credential store.
CREDENTIAL_STORE_FILE = os.path.join(
	PROJECT_ROOT,
	API_NAME + '.dat',
)


ARGS_FILE = os.path.join(
	CONFIG_ROOT,
	'file2.csv'
)

CLIENT_SECRET_FILE = os.path.join(
	CONFIG_ROOT,
	'client_secret_827029712124-5i2d5vmkeeeqsqs5mnqdpeiotls63j20.apps.googleusercontent.com.json',
)

INPUT_FILE = '/Users/peiyan/Desktop/peiyan.csv'