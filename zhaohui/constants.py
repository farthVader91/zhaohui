import os

API_NAME = 'dfareporting'   
API_VERSION = 'v2.6'
API_SCOPES = ['https://www.googleapis.com/auth/dfareporting',
              'https://www.googleapis.com/auth/dfatrafficking']

# Filename used for the credential store.
CREDENTIAL_STORE_FILE = API_NAME + '.dat'

ARGS_FILE = '/Users/peiyan/Documents/MightyHive/DCM_Trafficking/file2.csv'

CLIENT_SECRET_FILE = os.path.join(
	'/Users/peiyan/Documents/MightyHive/DCM_Trafficking',
	'client_secret_827029712124-5i2d5vmkeeeqsqs5mnqdpeiotls63j20.apps.googleusercontent.com.json',
)