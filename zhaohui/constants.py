import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #Why does it this way and also whhere is __file__
CONFIG_ROOT = '/Users/peiyan/Documents/MightyHive/DCM_Trafficking/'

API_NAME = 'dfareporting'   
API_VERSION = 'v2.6'
API_SCOPES = ['https://www.googleapis.com/auth/dfareporting',
              'https://www.googleapis.com/auth/dfatrafficking']

# Filename used for the credential store.
CREDENTIAL_STORE_FILE = os.path.join( #the dat file, does it require my computer to use it? once the dat file is there, it will be used all the time?
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

INPUT_FILE = '/Users/peiyan/Desktop/peiyan.csv' #why handle it different than args_file or client_secret_file?

CREATIVE_TYPES = [
    "DISPLAY",
    "INSTREAM_VIDEO",
    "BRAND_SAFE_DEFAULT_INSTREAM_VIDEO",
    "CUSTOM_DISPLAY",
    "CUSTOM_DISPLAY_INTERSTITIAL",
    "DISPLAY_IMAGE_GALLERY",
    "DISPLAY_REDIRECT",
    "FLASH_INPAGE",
    "HTML5_BANNER",
    "IMAGE",
    "INSTREAM_VIDEO_REDIRECT",
    "INTERNAL_REDIRECT",
    "INTERSTITIAL_INTERNAL_REDIRECT",
    "RICH_MEDIA_DISPLAY_BANNER",
    "RICH_MEDIA_DISPLAY_EXPANDING",
    "RICH_MEDIA_DISPLAY_INTERSTITIAL",
    "RICH_MEDIA_DISPLAY_MULTI_FLOATING_INTERSTITIAL",
    "RICH_MEDIA_IM_EXPAND",
    "RICH_MEDIA_INPAGE_FLOATING",
    "RICH_MEDIA_MOBILE_IN_APP",
    "RICH_MEDIA_PEEL_DOWN",
    "VPAID_LINEAR_VIDEO",
    "VPAID_NON_LINEAR_VIDEO",
]