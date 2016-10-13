import pandas as pd

from zhaohui.constants import CREATIVE_TYPES
from flask import redirect

class BaseAd(object):
    def __init__(self, placement, name, custom_url, _type, start_time, end_time, rows):
        self.placement = placement
        self.name = name
        self.custom_url = custom_url if pd.notnull(custom_url) else self.placement.dirsite.campaign.default_url
        self._type = _type if pd.notnull(_type) else "AD_SERVING_STANDARD_AD"
        start_time = start_time if pd.notnull(start_time) else pd.datetime.strptime(self.placement.dirsite.campaign.startdate, '%Y-%m-%d')
        self.start_time = start_time.strftime('%Y-%m-%d')
        end_time = end_time if pd.notnull(end_time) else (pd.datetime.strptime(self.placement.dirsite.campaign.enddate, '%Y-%m-%d') + pd.Timedelta('1 day'))
        self.end_time = end_time.strftime('%Y-%m-%d')
        self.rows = rows

        self._id = None


    def make_generic_payload(self):
        return { 
            'active': 'true',
            'name': self.name,
            'campaignId': self.placement.dirsite.campaign._id,
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
                    'placementId': self.placement._id,
                },
            ],
            'startTime': '%sT04:00:00Z' % self.start_time,
            'endTime': '%sT04:59:00Z' % self.end_time,
            'type': self._type,
        }


    def get_ad_id(self, service, profile_id):
        ad_id = None
        request = service.ads().list(
            profileId=profile_id,
            placementIds=self.placement._id, 
            searchString=self.name,
        )
        response = request.execute()
    
        ads = response.get('ads', [])
        if ads:
            ad_id = int(ads[0].get("id"))

        return ad_id


    def _create(self, service, profile_id):
        request = service.ads().insert(
            profileId=profile_id,
            body=self.make_payload(),
        )
        ad_info = request.execute()
        ad_id = int(ad_info.get('id'))
        self._id = ad_id
        print '{0} created!'.format(self)
        return ad_id        


    def create(self, service, profile_id):
        ad_id = self.get_ad_id(service, profile_id)
        if ad_id is not None:
            print "{0} already exists".format(self)
            self._id = ad_id
            return ad_id
        self._create(service, profile_id)


class DefaultAd(BaseAd):
    def make_creative_rotation(self, service, profile_id):
        assignments_container = []
        for _, row in self.rows.iterrows():
            request = service.creatives().list(
                profileId=profile_id, 
                campaignId=self.placement.dirsite.campaign._id, 
                searchString=row.creative_name,
            ) 
            response = request.execute()
                    
            creatives = response.get('creatives', [])
            if not creatives:
                # throw an exception if creative does not exist
                raise Exception('Creative-%s has not been created' % (row.creative_name))

            creative_id = int(creatives[0]["idDimensionValue"]["value"])

            assignments_container.append({
                'active': 'true',
                'creativeId': creative_id,
                'clickThroughUrl': {
                    'defaultLandingPage': 'false',
                    "customClickThroughUrl": self.custom_url
                }
            })

        rot_type = row.rotation_type
        rot_type = rot_type if not pd.isnull(rot_type) else "CREATIVE_ROTATION_TYPE_RANDOM"
        rot_weight = row.rotation_weight
        rot_weight = rot_weight if not pd.isnull(rot_weight) else "WEIGHT_STRATEGY_EQUAL"

        creative_rotation = {
            'creativeAssignments': assignments_container,
            'type': rot_type,  #CREATIVE_ROTATION_TYPE_SEQUENTIAL
            'weightCalculationStrategy': rot_weight #"WEIGHT_STRATEGY_CUSTOM",
            #"WEIGHT_STRATEGY_EQUAL",  #"WEIGHT_STRATEGY_HIGHEST_CTR" ,#"WEIGHT_STRATEGY_OPTIMIZED"
        }

        return creative_rotation


    def make_payload(self):
        payload = self.make_generic_payload()
        return payload

    def _create(self, service, profile_id):
        payload = self.make_payload()
        creative_rotation = self.make_creative_rotation(service, profile_id)
        payload.update({
            'creativeRotation': creative_rotation,
        })

        request = service.ads().insert(
            profileId=profile_id,
            body=payload,
        )
        ad_info = request.execute()
        ad_id = int(ad_info.get('id'))
        self._id = ad_id
        print '{0} created!'.format(self)
        return ad_id        


    def __str__(self):
        return 'DefaultAd-{0.name}'.format(self)


class TrackingAd(BaseAd):
    def __init__(self, *args, **kwargs):
        super(TrackingAd, self).__init__(*args, **kwargs)
        self.creative_id = None


    def create_creative(self, service, profile_id):
        creative = {
            "advertiserId": self.placement.dirsite.campaign.advertiser_id,
            "type": "TRACKING_TEXT",
            "name": "Tracking Ad",
            'active': "true"
        }

        request = service.creatives().insert(
            profileId=profile_id, 
            body=creative,
        )

        creative = request.execute()
        print "creative has been created"

        self.creative_id = int(creative["idDimensionValue"]["value"])

        return creative


    def associate_creative_to_campaign(self, service, profile_id):
        if self.creative_id is None:
            raise Exception('Create creative first before calling this function!')
        association = {
            'creativeId': [self.creative_id]
        }
        request = service.campaignCreativeAssociations().insert(
            profileId=profile_id,
            campaignId=self.placement.dirsite.campaign._id,
            body=association,
        )

        # Execute request and print response.
        association = request.execute()
        print "association has been made"
        return association


    def make_creative_rotation(self, service, profile_id):
        self.create_creative(service, profile_id)
        self.associate_creative_to_campaign(service, profile_id)
        creative_assignment = {
            'active': 'true',
            'creativeId': self.creative_id,
            'clickThroughUrl': {
                'defaultLandingPage': 'false',
                "customClickThroughUrl": self.custom_url,
            }
        }
        creative_rotation = {
            'creativeAssignments': [creative_assignment],
            'type': 'CREATIVE_ROTATION_TYPE_RANDOM',
            'weightCalculationStrategy': 'WEIGHT_STRATEGY_EQUAL'
        }

        return creative_rotation


    def make_payload(self):
        payload = self.make_generic_payload()
        return payload


    def _create(self, service, profile_id):
        payload = self.make_payload()
        creative_rotation = self.make_creative_rotation(service, profile_id)
        payload.update({
            'creativeRotation': creative_rotation,
        })

        request = service.ads().insert(
            profileId=profile_id,
            body=payload,
        )
        ad_info = request.execute()
        ad_id = int(ad_info.get('id'))
        self._id = ad_id
        print '{0} created!'.format(self)
        return ad_id        


    def __str__(self):
        return 'TrackingAd-{0.name}'.format(self)


class ClickTrackerAd(BaseAd):
    def __init__(self, *args, **kwargs):
        dynamic_click_tracker = kwargs.pop('dynamic_click_tracker', "False")
        super(ClickTrackerAd, self).__init__(*args, **kwargs)
        self.dynamic_click_tracker = dynamic_click_tracker


    def make_payload(self):
        payload = self.make_generic_payload()
        if self.dynamic_click_tracker != True:
            self.dynamic_click_tracker = "False"
            payload.pop('active', None)
        payload.update({
            'dynamicClickTracker': self.dynamic_click_tracker,
        })
        return payload


    def __str__(self):
        return 'ClickTrackerAd-{0.name}'.format(self)


class AdFactory(object):
    @staticmethod
    def make_ad(placement, rows):
        row = rows.iloc[0]
        if row.ad_type == 'AD_SERVING_CLICK_TRACKER':
            return ClickTrackerAd(
                placement=placement,
                name=row.ad_name,
                custom_url=row.custom_url,
                _type=row.ad_type,
                start_time=row.Ad_start_date,
                end_time=row.Ad_end_date,
                dynamic_click_tracker=row.dynamicClickTracker,
                rows=rows,
            )
        elif row.ad_type == 'AD_SERVING_TRACKING':
            return TrackingAd(
                placement=placement,
                name=row.ad_name,
                custom_url=row.custom_url,
                _type=row.ad_type,
                start_time=row.Ad_start_date,
                end_time=row.Ad_end_date,
                rows=rows,
            )
        else:
            return DefaultAd(
                placement=placement,
                name=row.ad_name,
                custom_url=row.custom_url,
                _type=row.ad_type,
                start_time=row.Ad_start_date,
                end_time=row.Ad_end_date,
                rows=rows,
            )


class Placement(object):
    def __init__(self, dirsite, name, compatibility,
                width, height, rows):
        self.dirsite = dirsite
        self.name = name
        self.compatibility = compatibility if pd.notnull(compatibility) else "DISPLAY"
        self.width = width
        self.height = height
        self.rows = rows
        # id will be assigned later
        self._id = None


    def iter_ads(self):
        unique_ads = self.rows.ad_name.unique()
        ads = []
        for name in unique_ads:
            rows = self.rows[self.rows['ad_name'] == name]
            ads.append(
                AdFactory.make_ad(self, rows)
            )

        return ads


    def get_placement_id(self, service, profile_id):
        placement_id = None
        request = service.placements().list(
            profileId=profile_id, 
            campaignIds=self.dirsite.campaign._id,
            directorySiteIds=self.dirsite._id,
            searchString=self.name,
        )
        response = request.execute()
    
        placements = response.get('placements')
        if placements:
            placement_id = int(placements[0].get("id"))

        return placement_id


    def make_generic_payload(self):
        return {
            'name': self.name,
            'campaignId': self.dirsite.campaign._id,
            'compatibility': self.compatibility,
            'directorySiteId': self.dirsite._id,
            'size': {
                'width': self.width,
                'height': self.height

            },
            'paymentSource': 'PLACEMENT_AGENCY_PAID',
            'tagFormats': [
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
            ],
            'pricingSchedule': {
                'startDate': self.dirsite.campaign.startdate,
                'endDate': self.dirsite.campaign.enddate,
                'pricingType': 'PRICING_TYPE_CPM',
            }
        }


    def make_payload(self):
        payload = self.make_generic_payload()
        if self.compatibility == 'IN_STREAM_VIDEO':
            # remove 'size' key
            payload.pop('size', None) 

        return payload


    def create(self, service, profile_id):
        placement_id = self.get_placement_id(service, profile_id)
        if placement_id is not None:
            print "{0} already exists".format(self)
            self._id = placement_id
            return placement_id
        request = service.placements().insert(
            profileId=profile_id,
            body=self.make_payload(),
        )
        placement_info = request.execute()
        placement_id = int(placement_info.get('id'))
        self._id = placement_id
        print '{0} created!'.format(self)
        return placement_id


    def __str__(self):
        return 'Placement-{0.name}'.format(self)

class DirSite(object):
    def __init__(self, campaign, site_id, rows):
        self.campaign = campaign
        self._id = site_id
        self.rows = rows


    def iter_placements(self):
        unique_placement_names = self.rows.placement_name.unique()
        placements = []
        for name in unique_placement_names:
            rows = self.rows[self.rows["placement_name"] == name]
            row = rows.iloc[0]
            placements.append(
                Placement(
                    self,
                    row.placement_name,
                    row.compatibility,
                    row.width,
                    row.height,
                    rows,
                )
            )

        return placements


class Campaign(object):
    def __init__(self, name, advertiser_id, startdate, enddate, default_url, default_url_name, rows):
        self.name = name
        self.advertiser_id = advertiser_id
        self.startdate = startdate.strftime('%Y-%m-%d')
        self.enddate = enddate.strftime('%Y-%m-%d')
        self.default_url = default_url
        self.default_url_name = default_url_name
        self.rows = rows
        # id will be assigned later
        self._id = None
        self.archived = 'false'
        


    def make_payload(self):
        return {
            'name': self.name,
            'advertiserId': self.advertiser_id,
            'archived': self.archived,
            'startDate': self.startdate,
            'endDate': self.enddate,
        }


    def iter_dirsites(self):
        unique_site_ids = self.rows.directorySIte_ID.unique()
        dirsites = []
        for site_id in unique_site_ids:
            df = self.rows
            rows = df[df.directorySIte_ID == site_id]
            dirsites.append(
                DirSite(
                    self,
                    site_id,
                    rows,
                )
            )

        return dirsites


    @classmethod 
    def iter_campaigns(cls, dataframe):
        unique_campaign_names = dataframe["campaign_name"].unique()

        campaigns = []

        for name in unique_campaign_names:
            # extract any one row
            rows= dataframe[dataframe["campaign_name"] == name]
            row = rows.iloc[0]
            campaigns.append(
                cls( 
                    row.campaign_name,
                    row.Advertiser_id,
                    row.startdate,
                    row.enddate,
                    row.default_url,
                    "default_url_name",
                    rows
                )
            )
        
   

        return campaigns


    def get_campaign_id(self, service, profile_id):
        campaign_id = None
        request = service.campaigns().list(
            profileId=profile_id,
            searchString=self.name,
        )
        response = request.execute()

        campaigns = response.get('campaigns')
        if campaigns:
            campaign_id = int(campaigns[0].get("id"))

        return campaign_id


    def create(self, service, profile_id):
        # check if campaign exists
        campaign_id = self.get_campaign_id(service, profile_id)
        if campaign_id is not None:
            print "{0} already exists".format(self)
            self._id = campaign_id
            return campaign_id

        # campaign doesn't exist, let's create it
        request = service.campaigns().insert(
            profileId=profile_id,
            defaultLandingPageName=self.default_url_name,
            defaultLandingPageUrl=self.default_url,
            body=self.make_payload(),
        )
        # Execute request and print response.
        try:
            campaign_info = request.execute()
        except Exception as err:
            print err
            return
        

        campaign_id = int(campaign_info.get("id"))
        self._id = campaign_id
        print '{0} created!'.format(self)
        return campaign_id   


    def activate_default_ads(self, service, profile_id):
        request = service.ads().list(
            profileId=profile_id,
            campaignIds=self._id,
            searchString="Default",
        )

        activate_default = request.execute()
        ads = activate_default.get("ads", [])
        for ad in ads:
            if not ad['active']:
                body = {
                    'active': 'true',
                    'campaignIds': self._id,
                }
                request = service.ads().patch(
                    profileId=profile_id,
                    id=ad['id'],
                    body=body,
                )

                response = request.execute()
                print "activating default ad-%s" % (ad['id'],)

        print "all the default ads are set to active now!"


    def creative_campaign_association(self, profileId, service, i):
        association = {
            'creativeId': i
        }
        request = service.campaignCreativeAssociations().insert(profileId=profileId, 
                                                                campaignId=self._id, 
                                                                body=association)
        # Execute request and print response.
        association = request.execute()


    def assign_creatives(self, service, profile_id):
        unique_creative_names = {
            ele for ele in self.rows.creative_name.unique().tolist()
            if not pd.isnull(ele)
        }
        ids =[]
        for i in unique_creative_names:
            request = service.creatives().list(profileId = profile_id, 
                                               advertiserId = self.advertiser_id, 
                                               searchString = i) 
            response = request.execute()
            creative_id = int(response.get("creatives")[0].get("idDimensionValue").get("value"))
            ids.append(creative_id)

        for i in ids:
            self.creative_campaign_association(profile_id, service, i)


    def get_missing_creatives(self, service, profile_id):
        # get created creatives
        request = service.creatives().list(
            profileId=profile_id,
            campaignId=self._id,
            types=CREATIVE_TYPES,
        )
        response = request.execute()
        creatives = response.get('creatives', [])
        existing_creative_names = {
            ele['creativeAssets'][0]['assetIdentifier']['name']
            for ele in creatives
        }
        #response.get("creatives")[i].get("creativeAssets")[0].get('assetIdentifier').get("name")

        unique_creative_names = {
            ele for ele in self.rows.creative_name.unique().tolist()
            if not pd.isnull(ele)
        }


        missing_creatives = []
        for uname in unique_creative_names:
            for ename in existing_creative_names:
                if uname in ename:
                    break
            else:
                missing_creatives.append(uname)


        return missing_creatives


    def __str__(self):
        return 'Campaign-{0.name}'.format(self)