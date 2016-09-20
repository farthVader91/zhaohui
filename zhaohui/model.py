class BaseAd(object):
    def __init__(self, placement, custom_url, _type, start_time, end_time, *args, **kwargs):
        self.placement = placement
        self.custom_url = custom_url
        self._type = _type
        self.start_time = start_time
        self.end_time = end_time

    def make_generic_payload(self):
        return {
            'name': self.placement.name
            'campaignId': self.placement.campaign.id,
            'clickThroughUrl':{
                'customClickThroughUrl': self.custom_url,
            },
            'deliverySchedule': {
                'impressionRatio': '1',
                'priority': 'AD_PRIORITY_15',
            },
            'placementAssignments': [
                {
                    'active': 'true',
                    'placementId': placementid,
                },
            ],
            'startTime': '%sT04:00:00Z' % self.start_time,
            'endTime': '%sT03:59:00Z' % self.end_time,
            'type': self._type,
        }


class TrackingAd(BaseAd):
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


class ClickTrackerAd(BaseAd):
    def __init__(self, placement, _type, custom_url, dynamic_click_tracker):
        super(ClickTrackerAd, self).__init__(placement)
        self.dynamic_click_tracker = dynamic_click_tracker

    def make_dynamic_tracker_payload(self):
        payload = self.make_generic_payload()
        payload.update({
            'dynamicClickTracker': True,
        })
        return payload


    def make_static_tracker_payload(self):
        payload = self.make_generic_payload()
        payload.update({
            'dynamicClickTracker': False,
        })        
        return payload


    def make_payload(self):
        if self.dynamic_click_tracker == "True":
            # implies that it's a dynamic click tracker
            return self.make_dynamic_tracker_payload()
        else:
            # implies that it's a static click tracker
            return self.make_static_tracker_payload()            


class Placement(object):
    TAG_FORMATS = [
        'PLACEMENT_TAG_STANDARD',
        'PLACEMENT_TAG_STANDARD',
        'PLACEMENT_TAG_IFRAME_JAVASCRIPT',
        'PLACEMENT_TAG_IFRAME_ILAYER',
        'PLACEMENT_TAG_INTERNAL_REDIRECT',
        'PLACEMENT_TAG_JAVASCRIPT',
        'PLACEMENT_TAG_INTERSTITIAL_IFRAME_JAVASCRIPT',
        'PLACEMENT_TAG_INTERSTITIAL_INTERNAL_REDIRECT',
        'PLACEMENT_TAG_INTERSTITIAL_JAVASCRIPT',
        'PLACEMENT_TAG_CLICK_COMMANDS',
        'PLACEMENT_TAG_INSTREAM_VIDEO_PREFETCH',
        'PLACEMENT_TAG_TRACKING',
        'PLACEMENT_TAG_TRACKING_IFRAME',
        'PLACEMENT_TAG_TRACKING_JAVASCRIPT',
    ]

    def __init__(self, name, campaign, compatibility,
                 dir_site_id, width, height, startdate, enddate):
        self.name = name
        self.campaign = campaign
        self.compatibility = compatibility
        self.dir_site_id = dir_site_id
        self.width = width
        self.height = height
        self.startdate = startdate
        self.enddate = enddate
        # id will be assigned later
        self._id = None

    def make_creative_payload(self):
        return {
            "advertiserId": self.campaign.advertiser_id,
            "type": "TRACKING_TEXT",
            "name": "Tracking Ad4",
            'active': "true"
        }

    def make_creative_association_payload(self, profileId, service, creative, campaignid):
        association = {
            'creativeId': [int(creative.get("idDimensionValue").get("value"))]
        }
        request = service.campaignCreativeAssociations().insert(
            profileId=profileId, campaignId=campaignid, body=association)

        # Execute request and print response.
        association = request.execute()
        print "association has been made"
        return association


    request = service.creatives().insert(profileId = profileId, 
    body = creative )
    creative = request.execute()
    print "creative has been created"
    return creative


    def extract_ads(self, dataframe):


    def make_payload(self):
        pass


class Campaign(object):
    def __init__(self, name, advertiser_id, startdate, enddate, default_url, default_url_name):
        self.name = name
        self.advertiser_id = advertiser_id
        self.startdate = startdate
        self.enddate = enddate
        self.default_url = default_url
        self.default_url_name = default_url_name
        self.archived = 'false'

        self._created = False
        self.placement = None
        self._id = None


    def make_payload(self):
        return {
            'name': self.name,
            'advertiserId': self.advertiser_id,
            'archived': self.archived,
            'startDate': self.startdate,
            'endDate': self.enddate,
        }

    def extract_campaigns(self, dataframe):
        # returns an iterable of campaign instances

    def __str__(self):
        return 'Campaign-{0.name}'.format(self)


def extract_canonical_campaign(dataframe):
    """Returns an instance of a `Campaign` from a dataframe.
    """
    row = dataframe.iloc[0]
    campaign = Campaign(
        row.campaign_name,
        row.Advertiser_id,
        row.startdate,
        row.enddate,
        row.default_url,
        row.default_url_name,
    )
    return campaign


def extract_canonical_placement(dataframe):
    pass


class CampaignManager(object):
    def __init__(self, service, profile_id):
        self.service = service
        self.profile_id = profile_id


    def iter_unique_campaigns(self, dataframe):
        unique_campaign_names = dataframe["campaign_name"].unique()
        for name in unique_campaign_names:
            # extract any one row
            row = dataframe[dataframe["campaign_name"] == name].iloc[0]
            yield Campaign(
                row.campaign_name,
                row.Advertiser_id,
                row.startdate,
                row.enddate,
                row.default_url,
                row.default_url_name,
            )


    def get_campaign_id(self, campaign_name):
        campaign_id = None
        request = self.service.campaigns().list(
            profileId=self.profile_id,
            searchString=campaign_name,
        )
        response = request.execute()

        campaigns = response.get('campaigns')
        if campaigns:
            campaign_id = int(campaigns[0].get("id"))

        return campaign_id


    def create_click_tracking_ad(self, ad):
        request = self.service.ads().insert(
            profileId=self.profile_id,
            body=ad.make_payload())

        # Execute request and print response.
        response = request.execute()
        return response

    def create_tracking_ad(self, ad):



    def create_creative(self, placement):
        request = service.creatives().insert(
            profileId=self.profile_id, 
            body=placement.make_creative_payload(),
        )
        creative = request.execute()
        return creative


    def associate_creative_to_campaign(self, campaign, creative):
        creative_id = creative.get("idDimensionValue").get("value")
        association = {
            'creativeId': [int(creative_id)],
        }
        request = service.campaignCreativeAssociations().insert(
            profileId=self.profile_id,
            campaignId=campaign.id,
            body=association,
        )
        # Execute request and print response.
        association = request.execute()
        print "association has been made"
        return association


    def create_campaign(self, campaign):
        # check if campaign exists
        campaign_id = self.get_campaign_id(campaign.name)
        if campaign_id is not None:
            print "{0} already exists".format(campaign)
            return campaign_id

        # campaign doesn't exist, let's create it
        request = self.service.campaigns().insert(
            profileId=self.profile_id,
            defaultLandingPageName=campaign.default_url_name,
            defaultLandingPageUrl=campaign.default_url,
            body=campaign.make_payload(),
        )
        # Execute request and print response.
        campaign_info = request.execute()
        campaign_id = int(campaign_info.get("id"))
        print '{0} created!'.format(campaign)
        return campaign_id   

def main():
    # extract canonical campaign from dataframe
    # create a campaign; get campaign_id
    # extract canonical placements from dataframe
    # for each placement:
    #   create placement
    #   for each placement row:
    #       create ad


if __name__ == '__main__':
    # extract canonical campaign first    
    inputs = pd.read_csv(open("/Users/peiyan/Desktop/peiyan.csv", "rU")) #Read from user's file
    campaign = extract_canonical_campaign(inputs)
    # create the campaign if it doesn't already exist
    service, profile_id = oauth()
    manager = CampaignManager(service, profile_id)
    manager.create_campaign(campaign)