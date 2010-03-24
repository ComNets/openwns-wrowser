import custom
import parameters

class Scenario:
    
    def __init__(self, scenarioID):
        self.scenarioID = scenarioID
        # Is set later
        self.parameterSet = None



def getScenariosForCampaign(campaign):

    sid = custom.query("SELECT DISTINCT(scenario_id) FROM parameters WHERE campaign_id = %d" % campaign.campaignID, campaign)
    result = []

    for row in sid:
        scen = Scenario(row[0])
        pa = parameters.getParameterSet(campaign, scen)
        scen.parameterSet = pa
        result.append(scen)

    return result
