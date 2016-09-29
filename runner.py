import ipdb 
import pandas as pd

from zhaohui.utils import get_service_and_profile_id
from zhaohui.constants import INPUT_FILE
from zhaohui.models import Campaign


def main():
	service, profile_id = get_service_and_profile_id()
	# get hold of the dataframe
	inputs = pd.read_csv(INPUT_FILE)
	# make campaigns
	for campaign in Campaign.iter_campaigns(inputs):
		# create the campaign
		campaign.create(service, profile_id)# create all placements
		campaignrows = inputs[inputs["campaign_name"] == campaign.name]
		unique_site_id = campaignrows.directorySIte_ID.unique()

		campaign.checkcreatives(service, profile_id, campaignrows)

		

		for site_id in unique_site_id:
			siterows = campaignrows[campaignrows["directorySIte_ID"] == site_id]

			for placement in campaign.iter_placements(siterows):
				placement.create(service, profile_id)# create all ads
				placementrows = siterows[siterows["placement_name"] == placement.name]

				for ad in placement.iter_ads(placementrows):
					try:
						ad.create(service, profile_id)
					except Exception as err:
						print 'Could not create %s because: %s' % (ad, err)


		campaign.activate(service, profile_id)


if __name__ == '__main__':
	main()