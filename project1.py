### This version completes 1.Only requires unique Placements not Ads 2. Creating Standard Ad 3. Creating Click Tracker -Static and Dynamic
#4.Tracking ad - Using Platform Ad instead of 1X1 Ad
#
import argparse
import os
import sys

from googleapiclient import discovery
import httplib2
from oauth2client import client
from oauth2client import file as oauthFile
from oauth2client import tools
import csv
import pandas as pd

API_NAME = 'dfareporting'   
API_VERSION = 'v2.6'
API_SCOPES = ['https://www.googleapis.com/auth/dfareporting',
              'https://www.googleapis.com/auth/dfatrafficking']

# Filename used for the credential store.
CREDENTIAL_STORE_FILE = API_NAME + '.dat'

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



def create_campaign( service, profileId, row):
    
    #check if the camapign has already existed
    

    request = service.campaigns().list(profileId = profileId, searchString = row.campaign_name)
    response = request.execute()
    
    if response.get("campaigns") != []:
        print "this is a campaign that has already been created"
        campaignid = int(response.get("campaigns")[0].get("id"))
        return campaignid
            
    else:
        print "this is a new campaign"
        campaign = {
        'name': row.campaign_name,
        'advertiserId': row.Advertiser_id,
        'archived': 'false',
        'startDate': row.startdate,
        'endDate': row.enddate
        }
        request = service.campaigns().insert(
            profileId=profileId, defaultLandingPageName= row.default_url_name,
            defaultLandingPageUrl=row.default_url, body=campaign)

        # Execute request and print response.
        campaigninfo = request.execute()
        campaignid = int(campaigninfo.get("id"))
        return campaignid   
    

def create_placement(profileId, service, campaignid, row):
    
    
    request = service.placements().list(profileId = profileId, 
                                        campaignIds = campaignid,
                                        searchString = row.placement_name)
    response = request.execute()
    
    if response.get("placements") != []:
        print "this is a placement that has already been created"
        placementid = int(response.get("placements")[0].get("id"))
        return placementid
    
    else:
        if (row.compatibility != "IN_STREAM_VIDEO"):
            
            placement = {
                'name': row.placement_name,
                'campaignId': campaignid,
                'compatibility': row.compatibility,#options of DISPLAY, DISPLAY_INTERSTITIAL, AND IN_STREAM_VIDEO
                'directorySiteId': row.directorySIte_ID,
                'size': {
                    'width': row.width,
                    'height': row.height

                },
                'paymentSource': 'PLACEMENT_AGENCY_PAID',
                'tagFormats': ['PLACEMENT_TAG_STANDARD',
                               "PLACEMENT_TAG_STANDARD",
                               "PLACEMENT_TAG_IFRAME_JAVASCRIPT",
                               "PLACEMENT_TAG_IFRAME_ILAYER",
                               "PLACEMENT_TAG_INTERNAL_REDIRECT",
                               "PLACEMENT_TAG_JAVASCRIPT",
                               "PLACEMENT_TAG_INTERSTITIAL_IFRAME_JAVASCRIPT",
                               "PLACEMENT_TAG_INTERSTITIAL_INTERNAL_REDIRECT",
                               "PLACEMENT_TAG_INTERSTITIAL_JAVASCRIPT",
                               "PLACEMENT_TAG_CLICK_COMMANDS",
                               "PLACEMENT_TAG_INSTREAM_VIDEO_PREFETCH",
                               "PLACEMENT_TAG_TRACKING",
                               "PLACEMENT_TAG_TRACKING_IFRAME",
                               "PLACEMENT_TAG_TRACKING_JAVASCRIPT"]
        }
            
            
        else:
            placement = {
                'name': row.placement_name,
                'campaignId': campaignid,
                'compatibility': row.compatibility,#options of DISPLAY, DISPLAY_INTERSTITIAL, AND IN_STREAM_VIDEO
                'directorySiteId': row.directorySIte_ID,
#                 'size': {
#                     'width': row.width,
#                     'height': row.height

#                 },
                'paymentSource': 'PLACEMENT_AGENCY_PAID',
                'tagFormats': ['PLACEMENT_TAG_STANDARD',
                               "PLACEMENT_TAG_STANDARD",
                               "PLACEMENT_TAG_IFRAME_JAVASCRIPT",
                               "PLACEMENT_TAG_IFRAME_ILAYER",
                               "PLACEMENT_TAG_INTERNAL_REDIRECT",
                               "PLACEMENT_TAG_JAVASCRIPT",
                               "PLACEMENT_TAG_INTERSTITIAL_IFRAME_JAVASCRIPT",
                               "PLACEMENT_TAG_INTERSTITIAL_INTERNAL_REDIRECT",
                               "PLACEMENT_TAG_INTERSTITIAL_JAVASCRIPT",
                               "PLACEMENT_TAG_CLICK_COMMANDS",
                               "PLACEMENT_TAG_INSTREAM_VIDEO_PREFETCH",
                               "PLACEMENT_TAG_TRACKING",
                               "PLACEMENT_TAG_TRACKING_IFRAME",
                               "PLACEMENT_TAG_TRACKING_JAVASCRIPT"]
            
          }  
               
        placement['pricingSchedule'] = {
            'startDate': row.startdate,
            'endDate': row.enddate,
            'pricingType': 'PRICING_TYPE_CPM'
        }
        request = service.placements().insert(profileId=profileId, body=placement)

        # Execute request and print response.
        placementinfo = request.execute()
        placementid = int(placementinfo.get('id'))
        return placementid



def creative_campaign_association(profileId, service, creative, campaignid):
   
    association = {
        'creativeId': [int(creative.get("idDimensionValue").get("value"))]
    }
    request = service.campaignCreativeAssociations().insert(
        profileId=profileId, campaignId=campaignid, body=association)

    # Execute request and print response.
    association = request.execute()
    print "association has been made"
    return association
    

def create_creatives(profileId, service, row):
    creative = {
    "advertiserId": row.Advertiser_id,
    "type": "TRACKING_TEXT",
    "name": "Tracking Ad4",
    'active': "true"
    }

    request = service.creatives().insert(profileId = profileId, 
    body = creative )
    creative = request.execute()
    print "creative has been created"
    return creative


def creative_campaign_association(profileId, service, creative, campaignid):
   
    association = {
        'creativeId': [int(creative.get("idDimensionValue").get("value"))]
    }
    request = service.campaignCreativeAssociations().insert(
        profileId=profileId, campaignId=campaignid, body=association)

    # Execute request and print response.
    association = request.execute()
    print "association has been made"
    return association
    

def create_TrackingAd(profileId, service, row, campaignid, placementid, ad_row):
    creative = create_creatives(profileId, service, row)
    creative_campaign_association(profileId, service, creative, campaignid)
    
    placement_assignment = {
        'active': 'true',
        'placementId': placementid,
    }

    delivery_schedule = {
        'impressionRatio': '1',
        'priority': 'AD_PRIORITY_15'
    }
    creative_assignment = {
        'active': 'true',
        'creativeId': int(creative.get("idDimensionValue").get("value")),
        'clickThroughUrl': {
            'defaultLandingPage': 'false',
            "customClickThroughUrl": ad_row.custom_url.iloc[0]
            }
        }
        

    creative_rotation = {
        'creativeAssignments': [creative_assignment],
        'type': 'CREATIVE_ROTATION_TYPE_RANDOM',  #CREATIVE_ROTATION_TYPE_SEQUENTIAL
        'weightCalculationStrategy': 'WEIGHT_STRATEGY_EQUAL'#"WEIGHT_STRATEGY_CUSTOM",
                    #"WEIGHT_STRATEGY_EQUAL",  #"WEIGHT_STRATEGY_HIGHEST_CTR" ,#"WEIGHT_STRATEGY_OPTIMIZED"
      }
    
    ad = {'active': 'true',
          'campaignId': campaignid,
          #'creativeId': 73942622,
          'creativeRotation': creative_rotation,
          'deliverySchedule': delivery_schedule,
          'startTime': '%sT04:00:00Z' % row.Ad_start_date,
          'endTime': '%sT03:59:00Z' % row.Ad_end_date,
          'name': row.ad_name,
          'placementAssignments': [placement_assignment],
          'type': "Ad_SERVING_TRACKING" #AD_SERVING_CLICK_TRACKER"
                                                #"AD_SERVING_DEFAULT_AD"
                                                #"AD_SERVING_STANDARD_AD"
                                                #"AD_SERVING_TRACKING"
         }
    

    request = service.ads().insert(profileId=profileId, body=ad)
    response = request.execute()
    return response

                
def create_ClickTracker(profileId, service, row, campaignid, placementid, ad_row):

   
    
    placement_assignment = {
        'active': 'true',
        'placementId': placementid,
    }

    delivery_schedule = {
        'impressionRatio': '1',
        'priority': 'AD_PRIORITY_15'
    }
#     creative_assignment = {
#         'active': 'true',
#         'creativeId': int(creative.get("idDimensionValue").get("value"))
# #         'clickThroughUrl': {
# #             'defaultLandingPage': 'false',
# #             "customClickThroughUrl": custom_url
# #             }
#         }
   
#     creative_rotation = {
#         'creativeAssignments': creative_assignment,
#         'type': 'CREATIVE_ROTATION_TYPE_RANDOM',  #CREATIVE_ROTATION_TYPE_SEQUENTIAL
#         'weightCalculationStrategy': 'WEIGHT_STRATEGY_OPTIMIZED'#"WEIGHT_STRATEGY_CUSTOM",
#                     #"WEIGHT_STRATEGY_EQUAL",  #"WEIGHT_STRATEGY_HIGHEST_CTR" ,#"WEIGHT_STRATEGY_OPTIMIZED"

#                 }
    
    if (str(ad_row.dynamicClickTracker.iloc[0]) == "True"): 
        print "this is dynamic click tracker"
        
        ad = {
            'active': 'true',
            #'creativeId': int(creative.get("idDimensionValue").get("value")),
            'campaignId': campaignid,
            'clickThroughUrl':{"customClickThroughUrl": ad_row.custom_url.iloc[0]},
            #'creativeRotation': creative_rotation,
            'deliverySchedule': delivery_schedule,
            'name': row.ad_name,
            'placementAssignments': [placement_assignment],
            'startTime': '%sT04:00:00Z' % row.Ad_start_date,
            'endTime': '%sT03:59:00Z' % row.Ad_end_date,
            "dynamicClickTracker": True,
            'type': "AD_SERVING_CLICK_TRACKER"
                                                    #row.ad_type #AD_SERVING_CLICK_TRACKER"
                                                    #"AD_SERVING_DEFAULT_AD"
                                                    #"AD_SERVING_STANDARD_AD"
                                                    #"AD_SERVING_TRACKING"

        }

    else:
        print "this is static click tracker"
        ad = {'active': 'false',
              'campaignId': campaignid,
              'clickThroughUrl':{"customClickThroughUrl": ad_row.custom_url.iloc[0]},
              'deliverySchedule': delivery_schedule,
              'startTime': '%sT04:00:00Z' % row.Ad_start_date,
              'endTime': '%sT03:59:00Z' % row.Ad_end_date,
              'name': row.ad_name,
              'placementAssignments': [placement_assignment],
              "dynamicClickTracker": "false",
              'type': "AD_SERVING_CLICK_TRACKER"
                                                    #row.ad_type #AD_SERVING_CLICK_TRACKER"
                                                    #"AD_SERVING_DEFAULT_AD"
                                                    #"AD_SERVING_STANDARD_AD"
         }                            #"AD_SERVING_TRACKING"
        
    request = service.ads().insert(profileId=profileId, body=ad)

                # Execute request and print response.
    response = request.execute()
    return response
            

def create_ads(service, profileId, row, campaignid, placementid, relevant_row):
    
    for i in range(0, len(relevant_row.ad_name.unique())):
        ad_name = relevant_row.ad_name.unique()[i]
        ad_row = relevant_row.loc[relevant_row["ad_name"] == ad_name]
        
    
        request = service.ads().list(profileId = profileId, placementIds = placementid, 
                                 searchString = ad_name)
        response = request.execute()
    
    
        if response.get("ads") != []:
            #creative_ids_from_the_ad = []
            print "The ad has already been created"
            
            

    
        else:
            
            print "this is a new ad"
           
     
            if (ad_row.ad_type.iloc[0] == "AD_SERVING_CLICK_TRACKER"):
                print "this is a click tracker ad"
                response = create_ClickTracker(profileId, service, row, campaignid, placementid, ad_row)
                return response
                
            
            if (ad_row.ad_type.iloc[0] == "AD_SERVING_TRACKING"):
                print "this is tracking ad"
                response = create_TrackingAd(profileId, service, row, campaignid, placementid, ad_row)
                return response
            
           
                
            
                
                
             
                
            else:
                assignments_container = []
                i = 0
                for i in range(0, len(ad_row)):
                    request = service.creatives().list(profileId = profileId, 
                                                   campaignId = campaignid, 
                                                   searchString = ad_row.creative_name.iloc[i]) 
                    response = request.execute()
                    
                
                    
                    creative_id = int(response.get("creatives")[0].get("idDimensionValue").get("value"))
                    custom_url = ad_row.custom_url.iloc[i]
                    creative_assignment = {
                        'active': 'true',
                        'creativeId': creative_id,
                        'clickThroughUrl': {
                            'defaultLandingPage': 'false',
                            "customClickThroughUrl": custom_url
                        }
                    }
                    assignments_container.append(creative_assignment)

                creative_rotation = {
                    'creativeAssignments': assignments_container,
                    'type': ad_row.rotation_type.iloc[i],  #CREATIVE_ROTATION_TYPE_SEQUENTIAL
                    'weightCalculationStrategy': ad_row.rotation_weight.iloc[i]#"WEIGHT_STRATEGY_CUSTOM",
                    #"WEIGHT_STRATEGY_EQUAL",  #"WEIGHT_STRATEGY_HIGHEST_CTR" ,#"WEIGHT_STRATEGY_OPTIMIZED"

                }
                placement_assignment = {
                    'active': 'true',
                    'placementId': placementid,
                }

                delivery_schedule = {
                    'impressionRatio': '1',
                    'priority': 'AD_PRIORITY_15'
                }

            # Construct and save ad.
                ad = {
                    'active': 'true',
                    'campaignId': campaignid,
                    'creativeRotation': creative_rotation,
                    'deliverySchedule': delivery_schedule,
                    'startTime': '%sT04:00:00Z' % row.Ad_start_date,
                    'endTime': '%sT03:59:00Z' % row.Ad_end_date,
                    'name': ad_row.ad_name.iloc[i],
                    'placementAssignments': [placement_assignment],
                    'type': ad_row.ad_type.iloc[0] #AD_SERVING_CLICK_TRACKER"
                                                #"AD_SERVING_DEFAULT_AD"
                                                #"AD_SERVING_STANDARD_AD"
                                                #"AD_SERVING_TRACKING"
                }
                request = service.ads().insert(profileId=profileId, body=ad)
                
                response = request.execute()
                return response
                
    return response

def activate(service, profileId, campaignid):
    request = service.ads().list(profileId = profileId,  campaignIds = campaignid,
                                 searchString = "Default Web Ad")
    activate_default = request.execute()
    
    for i in range(0,len(activate_default.get("ads")) ):
        if activate_default.get("ads")[i].get("active") == False:
            ads = {
                'active': 'True',
                "campaignIds":campaignid
            
            }
            request = service.ads().patch(profileId = profileId, id = int(activate_default.get("ads")[i].get("id")),
                                 body=ads)
            response = request.execute()
   
        
        else:
            print "all the default ads are set to active now!"

#1
inputs = pd.read_csv(open("/Users/peiyan/Desktop/peiyan.csv", "rU")) #Read from user's file
inputs

#2
unique_ad_names = inputs["placement_name"].unique().tolist()# find all the unique ads name 
unique_ad_names

row = inputs[inputs["placement_name"] == unique_ad_names[0] ].head(1).iloc[0]
row

[service, profileId] = oAuth() #shake hands with Oath
campaignid = create_campaign(service, profileId, row) #create campaign and pass back the created campaign id
#4 
#Upload creatives
#5
i = 0
for i in range(0,len(unique_ad_names)):  
    row = inputs[inputs["placement_name"] == unique_ad_names[i] ].head(1).iloc[0]
    placementid = create_placement(profileId, service, campaignid, row)
    relevant_row = inputs.loc[inputs['placement_name'] == unique_ad_names[i]]
    adinfo = create_ads(service, profileId, row, campaignid, placementid, relevant_row)
    

#6
activate_default = activate(service, profileId, campaignid) # all the default ads are being set to active now