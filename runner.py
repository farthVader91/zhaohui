import ipdb 
import pandas as pd

from zhaohui.utils import get_service_and_profile_id
from zhaohui.constants import INPUT_FILE
from zhaohui.models import Campaign


def main():
	service, profile_id = get_service_and_profile_id()
	# get hold of the dataframe
	inputs = pd.read_csv(
		INPUT_FILE,
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
	# make campaigns
	for campaign in Campaign.iter_campaigns(inputs):
		# create campaign
		campaign.create(service, profile_id)
		# get missing creatives have been uploaded
		missing_creatives = campaign.get_missing_creatives(service, profile_id)
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

		# finally, activate all default ads in the campaign
		# Note: Default ads are created automatically when you create an ad.
		campaign.activate_default_ads(service, profile_id)


if __name__ == '__main__':
	main()