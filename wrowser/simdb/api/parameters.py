import custom

class ParameterSet:

    def __init__(self, campaign, scenarioID):
        self.campaign = campaign
        self.scenarioID = scenarioID
        self.params = {}

def getParametersOfCampaign(campaign):

    p = custom.query("SELECT DISTINCT(parameter_name) FROM parameters WHERE campaign_id = %d" % campaign.campaignID, campaign)
    result = []

    for l in p:
        result.append(l[0])

    return result

def getParameterSet(campaign, scenario):

    p = custom.query("SELECT parameter_name, parameter_type, type_bool, type_integer, type_float, type_string "
                     "FROM parameters WHERE scenario_id = %d" % scenario.scenarioID, campaign)

    ps = ParameterSet(campaign, scenario.scenarioID)

    for l in p:
        paramname = str(l[0])

        if l[1] == "type_bool":
            ps.params[paramname] = bool(l[2])

        if l[1] == "type_integer":
            ps.params[paramname] = int(l[3])

        if l[1] == "type_float":
            ps.params[paramname] = float(l[4])

        if l[1] == "type_string":
            ps.params[paramname] = float(l[5])

    return ps
    
