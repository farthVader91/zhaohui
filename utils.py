import os
import pandas as pd
from uuid import uuid4

from gcloud import storage, datastore

import settings
from zhaohui.utils import get_service_and_profile_id
from zhaohui.models import Campaign
from zhaohui import constants
from datetime import datetime



os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(constants.CONFIG_ROOT, 'dcm trafficking-994418ffc74d.json')

def store_csv(file_obj):
	"""Creates a blob with a unique name and uploads onto Google Cloud Storage.
	Returns the blob object.
	"""
	file_obj.seek(0, 0)
	client = storage.Client()
	bucket = client.get_bucket(settings.GCS_BUCKET_NAME)
	df = pd.read_csv(file_obj)
	campaign_info = df.iloc[0]["Advertiser_id"].astype(str) + '-' + df.iloc[0]["campaign_name"]
	name = unicode(campaign_info +  "-" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	blob = bucket.blob(name, chunk_size=262144)
	blob.content_type = 'text/csv'
	file_obj.seek(0, 0)
	blob.upload_from_file(file_obj)
	blob.make_public()
	return blob


def make_campaign_entry(profile_id, email, blob, status, info):
	"""Makes an entry for the campaign being created.
	Information gets recorded in the DataStore in the google console
	"""
	client = datastore.Client()
	key = client.key('CampaignCreation')

	entity = datastore.Entity(key=key)
	entity['profile_id'] = profile_id
	entity['email'] = email
	entity['blob_name'] = unicode(blob.name)
	entity['blob_url'] = blob.media_link
	entity['completed'] = status
	entity['creation_time'] = unicode(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

	info_key = client.key('CreationResult')
	info_entity = datastore.Entity(key=info_key)
	info_entity['failed_ads'] = unicode(info)

	entity['info'] = info_entity

	client.put(entity)
	return True


def create_campaign(profile_id, file_obj):
	file_obj.seek(0, 0)
	service = get_service_and_profile_id()
	# get hold of the dataframe
	inputs = pd.read_csv(
		file_obj,
		parse_dates=[
			'startdate',
			'enddate',
			'Ad_start_date',
			'Ad_end_date',
		],
	)
	# split ad_size as width and height
	inputs = inputs.join(
		inputs.ad_size.str.split(
			'x', 1, expand=True
		).rename(
			columns={
				0: 'width',
				1: 'height',
			}
		)
	)
	failed_ads = set()
	all_good = True
	# make campaigns
	for campaign in Campaign.iter_campaigns(inputs):
		# create campaign
		campaign.create(service, profile_id)

		#Optional choice to assign creatives from Advertiser to campaign
		#campaign.assign_creatives(service, profile_id)
		# get missing creatives have been uploaded
		missing_creatives = campaign.get_missing_creatives(service, profile_id)
		if missing_creatives:
			print "Missing creatives!\n%s" % ('\n'.join(missing_creatives),)
		# iterate over unique directory sites
		for dir_site in campaign.iter_dirsites():
			# iterate over placemenets
			for placement in dir_site.iter_placements():
				# create placement
				placement.create(service, profile_id)
				# iterate over ads
				for ad in placement.iter_ads():
					try:
						# create ad
						ad.create(service, profile_id)
					except Exception as err:
						print 'Could not create %s because: %s' % (ad, err)
						failed_ads.add(ad.name)
						all_good = False

		# finally, activate all default ads in the campaign
		# Note: Default ads are created automatically when you create an ad.
		campaign.activate_default_ads(service, profile_id)

	return (all_good, failed_ads)