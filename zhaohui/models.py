class BaseAd(object):
    def __init__(self, placement, name, custom_url, _type, start_time, end_time):
        self.placement = placement
        self.name = name
        self.custom_url = custom_url
        self._type = _type
        self.start_time = start_time
        self.end_time = end_time

        self._id = None


    def make_generic_payload(self):
        return {
            'active': 'true',
            'name': self.name,
            'campaignId': self.placement.campaign._id,
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
            'endTime': '%sT03:59:00Z' % self.end_time,
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
    def __init__(self, *args, **kwargs):
        rows = kwargs.pop('creative_rows')
        super(DefaultAd, self).__init__(*args, **kwargs)
        self.creative_rows = rows


    def make_creative_rotation(self, service, profile_id):
        assignments_container = []
        for _, row in self.creative_rows.iterrows():
            request = service.creatives().list(
                profileId=profile_id, 
                campaignId=self.placement.campaign._id, 
                searchString=row.creative_name,
            ) 
            response = request.execute()
                    
            creative_id = int(
                response.get(
                    "creatives"
                )[0].get("idDimensionValue").get("value")
            )

            assignments_container.append({
                'active': 'true',
                'creativeId': creative_id,
                'clickThroughUrl': {
                    'defaultLandingPage': 'false',
                    "customClickThroughUrl": row.custom_url
                }
            })

        creative_rotation = {
            'creativeAssignments': assignments_container,
            'type': row.rotation_type,  #CREATIVE_ROTATION_TYPE_SEQUENTIAL
            'weightCalculationStrategy': row.rotation_weight#"WEIGHT_STRATEGY_CUSTOM",
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
            "advertiserId": self.placement.campaign.advertiser_id,
            "type": "TRACKING_TEXT",
            "name": "Tracking Ad4",
            'active': "true"
        }

        request = service.creatives().insert(
            profileId=profile_id, 
            body=creative,
        )

        creative = request.execute()
        print "creative has been created"

        self.creative_id = int(creative.get("idDimensionValue").get("value"))

        return creative


    def associate_creative_to_campaign(self, service, profile_id):
        if self.creative_id is None:
            raise Exception('Create creative first before calling this function!')
        association = {
            'creativeId': [self.creative_id]
        }
        request = service.campaignCreativeAssociations().insert(
            profileId=profile_id,
            campaignId=self.placement.campaign._id,
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
        dynamic_click_tracker = kwargs.pop('dynamic_click_tracker')
        super(ClickTrackerAd, self).__init__(*args, **kwargs)# please explain more on this
        self.dynamic_click_tracker = dynamic_click_tracker


    def make_dynamic_tracker_payload(self):
        payload = self.make_generic_payload()
        payload.update({
            'dynamicClickTracker': "True",
        })
        #payload.pop('active', None)
        return payload


    def make_static_tracker_payload(self):
        payload = self.make_generic_payload()
        payload.update({
            'dynamicClickTracker': False,
        })        
        payload.pop('active', None)
        return payload


    def make_payload(self):
        if self.dynamic_click_tracker == True:
            # implies that it's a dynamic click tracker
            return self.make_dynamic_tracker_payload()
        else:
            # implies that it's a static click tracker
            return self.make_static_tracker_payload()            


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
            )
        elif row.ad_type == 'AD_SERVING_TRACKING':
            return TrackingAd(
                placement=placement,
                name=row.ad_name,
                custom_url=row.custom_url,
                _type=row.ad_type,
                start_time=row.Ad_start_date,
                end_time=row.Ad_end_date,
            )
        else:
            return DefaultAd(
                placement=placement,
                name=row.ad_name,
                custom_url=row.custom_url,
                _type=row.ad_type,
                start_time=row.Ad_start_date,
                end_time=row.Ad_end_date,
                creative_rows=rows,
            )


class Placement(object):
    def __init__(self, campaign, name, compatibility,
                 dir_site_id, width, height):
        self.campaign = campaign
        self.name = name
        self.compatibility = compatibility
        self.dir_site_id = dir_site_id
        self.width = width
        self.height = height
        # id will be assigned later
        self._id = None


    def iter_ads(self, dataframe):
        unique_ads = dataframe[dataframe['placement_name'] == self.name].ad_name.unique()
        ads = []
        for name in unique_ads:
            rows = dataframe[dataframe['ad_name'] == name]
            ads.append(
                AdFactory.make_ad(self, rows)
            )

        return ads


    def get_placement_id(self, service, profile_id):
        placement_id = None
        request = service.placements().list(
            profileId=profile_id, 
            campaignIds=self.campaign._id,
            directorySiteIds = self.dir_site_id,
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
            'campaignId': self.campaign._id,
            'compatibility': self.compatibility,
            'directorySiteId': self.dir_site_id,
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
                'startDate': self.campaign.startdate,
                'endDate': self.campaign.enddate,
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


class Campaign(object):
    def __init__(self, name, advertiser_id, startdate, enddate, default_url, default_url_name):
        self.name = name
        self.advertiser_id = advertiser_id
        self.startdate = startdate
        self.enddate = enddate
        self.default_url = default_url
        self.default_url_name = default_url_name
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

    def iter_placements(self, dataframe):
        unique_placement_names = dataframe[dataframe["campaign_name"] == self.name].placement_name.unique()
        placements = []
        for name in unique_placement_names:
            row = dataframe[dataframe["placement_name"] == name].iloc[0]
            placements.append(#why for campaign we are using cls while for placements we are using self?
                Placement(
                    self,
                    row.placement_name,
                    row.compatibility,
                    row.directorySIte_ID,
                    row.width,
                    row.height,
                )
            )

        return placements


    @classmethod #why it says this?
    def iter_campaigns(cls, dataframe):#cls vs. self
        unique_campaign_names = dataframe["campaign_name"].unique()

        campaigns = []

        for name in unique_campaign_names:
            # extract any one row
            row = dataframe[dataframe["campaign_name"] == name].iloc[0]
            campaigns.append(
                cls(
                    row.campaign_name,
                    row.Advertiser_id,
                    row.startdate,
                    row.enddate,
                    row.default_url,
                    row.default_url_name,
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
        campaign_info = request.execute()
        campaign_id = int(campaign_info.get("id"))
        self._id = campaign_id
        print '{0} created!'.format(self)
        return campaign_id   

    def activate(self, service, profile_id):
        request = service.ads().list(profileId = profile_id,  campaignIds = self._id,
                                 searchString = "Default")

        activate_default = request.execute()
        for i in range(0,len(activate_default.get("ads")) ):
            if activate_default.get("ads")[i].get("active") == False:
                ads = {
                'active': 'True',
                "campaignIds":self._id
            }
                request = service.ads().patch(profileId = profile_id, id = int(activate_default.get("ads")[i].get("id")),
                                 body=ads)

                response = request.execute()
        
            else:
                print "all the default ads are set to active now!"


    def checkcreatives(self, service, profile_id, campaignrows):
        print "Please upload all your creatives to:", self.name, "if you haven't done so."
        unique_creative_names = campaignrows["creative_name"].unique()
        print unique_creative_names
        request = service.creatives().list(profileId = profile_id,  campaignId = self._id, types = #"DISPLAY" 
                                                                                                "INSTREAM_VIDEO" 
                                                                                                or "BRAND_SAFE_DEFAULT_INSTREAM_VIDEO"
                                                                                                or "CUSTOM_DISPLAY"
                                                                                                or "CUSTOM_DISPLAY_INTERSTITIAL"
                                                                                                or "DISPLAY_IMAGE_GALLERY"
                                                                                                or "DISPLAY_REDIRECT"
                                                                                                or "FLASH_INPAGE"
                                                                                                or "HTML5_BANNER"
                                                                                                or "IMAGE"
                                                                                                or "INSTREAM_VIDEO_REDIRECT"
                                                                                                or "INTERNAL_REDIRECT"
                                                                                                or "INTERSTITIAL_INTERNAL_REDIRECT"
                                                                                                or "RICH_MEDIA_DISPLAY_BANNER"
                                                                                                or "RICH_MEDIA_DISPLAY_EXPANDING"
                                                                                                or "RICH_MEDIA_DISPLAY_INTERSTITIAL"
                                                                                                or "RICH_MEDIA_DISPLAY_MULTI_FLOATING_INTERSTITIAL"
                                                                                                or "RICH_MEDIA_IM_EXPAND"
                                                                                                or "RICH_MEDIA_INPAGE_FLOATING"
                                                                                                or "RICH_MEDIA_MOBILE_IN_APP"
                                                                                                or "RICH_MEDIA_PEEL_DOWN"
                                                                                                or "VPAID_LINEAR_VIDEO"
                                                                                                or "VPAID_NON_LINEAR_VIDEO")
        response = request.execute()
        existing_creatives = []
        #print response.get("creatives")[13]

        for i in range(0, len(response.get("creatives"))):
            #if esponse.get("creatives")[i]
            creative_name = response.get("creatives")[i].get("creativeAssets")[0].get('assetIdentifier').get("name")
            existing_creatives.append(creative_name)
            i = i + 1
        print existing_creatives

        missing_creatives = []
        for creative_name in unique_creative_names:
            j = 0
            for j in range(0, len(unique_creative_names)):
                if creative_name not in existing_creatives[j]:
                    j = j + 1

                else:
                    break
        missing_creatives.append(creative_name)
        print "we are missing the following creatives ", missing_creatives
       

    def __str__(self):
        return 'Campaign-{0.name}'.format(self)



