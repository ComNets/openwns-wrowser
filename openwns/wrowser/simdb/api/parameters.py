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
        typename = l[1].rstrip()

        if typename == "type_bool":
            #print "Adding bool parameter %s:%s" % (paramname, l[2])
            ps.params[paramname] = bool(l[2])

        if typename == "type_integer":
            #print "Adding int parameter %s:%s" % (paramname, l[3])
            ps.params[paramname] = int(l[3])

        if typename == "type_float":
            #print "Adding float parameter %s:%s" % (paramname, l[4])
            ps.params[paramname] = float(l[4])

        if typename == "type_string":
            #print "Adding string parameter %s:%s" % (paramname, l[5])
            ps.params[paramname] = str(l[5])

    return ps
    
