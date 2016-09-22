import pandas as pd

from zhaohui.utils import get_service_and_profile_id
from zhaohui.constants import INPUT_FILE
from zhaohui.models import Campaign


def main():
	service, profile_id = get_service_and_profile_id()
	# get hold of the dataframe
	inputs = pd.read_csv(INPUT_FILE, 'rU')
	# make campaigns
	for campaign in Campaign.iter_campaigns(inputs):
		# create the campaign
		campaign.create(service, profile_id)
		# create all placements
		for placement in campaign.iter_placements(inputs):
			placement.create(service, profile_id)
			# create all ads
			for ad in placement.iter_ads(inputs):
				ad.create(service, profile_id)