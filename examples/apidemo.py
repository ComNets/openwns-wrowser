import wrowser.simdb.api as api

# First you need to get a campaign
# You can get it by title
c = api.getCampaignByTitle("The of your campaign as shown in wrowser")

# or you can use
#
# campaignlist = api.getCampaigns()
#
# to get all your campaigns

# Once you have the campaign you can fetch all the scenarios
s = api.getScenariosForCampaign(c)

from pylab import *

# You can retrieve entries from a PDF probe by using getPDF, getCDF or getCCDF
# Give it the probe name and the campaign
# In this example the CDFs for all scenarios are aggregated using the AVG function
# Use forScenarios to control which scenarios should be included
#
# If you omit forScenarios all scenarios of the campaign are used
# If you omit agg, no aggregation is performed and you get one CDF for each campaign
cdfs = api.getCDFs("top.total.window.incoming.bitThroughput_UT_PDF", c, forScenarios = s, agg="AVG")

# Now you can use that data for plotting
for x,y in cdfs:
    plot(array(x),array(y))

xlim(0.0, 1.0)
grid()
title("API Demo")
legend(["openWNS", "rocks", "Yeah!"])
xlabel("Downlink throughput [bps]")
ylabel("P(X < x)")
show()

# Checkout the api package for more.
