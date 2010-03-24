import custom

class ResultsInfo:

    def __init__(self):
        self.pdfProbes = []
        pass

def getResultsInfo(campaign):

    q = "SELECT DISTINCT(alt_name) FROM pd_fs WHERE campaign_ID=%d" % campaign.campaignID

    r = custom.query(q, campaign)

    ri = ResultsInfo()

    for row in r:
        ri.pdfProbes.append(row[0])

    return ri

def getPDFs(name, campaign, forScenarios=None, agg=None):
    return _getPDF("pdf", name, campaign, forScenarios, agg)

def getCDFs(name, campaign, forScenarios=None, agg=None):
    return _getPDF("cdf", name, campaign, forScenarios, agg)

def getCCDFs(name, campaign, forScenarios=None, agg=None):
    return _getPDF("ccdf", name, campaign, forScenarios, agg)

def _getPDF(what, name, campaign, forScenarios, agg):
    if forScenarios is None:
        forScenarios = getScenariosForCampaign(campaign)

    if agg is None:

        pdfs = []
        for scen in forScenarios:

            q = "SELECT VAL.x, VAL.%s FROM pdf_histograms VAL \
                 INNER JOIN(SELECT id, scenario_id FROM pd_fs WHERE scenario_id=%d AND alt_name='%s') AS probeResults \
                 ON VAL.probe_id = probeResults.id \
                 ORDER BY VAL.x" % (what, scen.scenarioID, name)

            r = custom.query(q, campaign)
               
            x = []
            y = []

            for row in r:
                x.append(row[0])
                y.append(row[1])

                
            pdfs.append((x,y))
        return pdfs
    else:
        scensql = "(" + ",".join([str(s.scenarioID) for s in forScenarios]) + ")"

        q = "SELECT AVG(VAL.x), %s(VAL.%s) FROM pdf_histograms VAL \
             INNER JOIN(SELECT id, scenario_id FROM pd_fs WHERE scenario_id IN %s AND alt_name='%s') AS probeResults \
             ON VAL.probe_id = probeResults.id \
             GROUP BY VAL.x \
             ORDER BY VAL.x;" % (agg, what, scensql, name)

        r = custom.query(q, campaign)
               
        x = []
        y = []

        for row in r:
            x.append(row[0])
            y.append(row[1])

        return [(x,y)]

