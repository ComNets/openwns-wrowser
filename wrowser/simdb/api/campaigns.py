import wrowser.simdb.Database as db
import wrowser.Configuration

class Campaign:

    def __init__(self, campaignID, title, description, dbSize, authorized):
        self.campaignID = campaignID
        self.title = title
        self.description = description
        self.dbSize = dbSize
        self.authorized = authorized

def getCampaigns():

    config = wrowser.Configuration.Configuration()
    config.read()

    db.Database.connectConf(config)
    db.Database.showAllCampaigns()
    cursor = db.Database.getCursor()
    cursor.execute('SELECT user_name, full_name, campaigns.id, title, description, ' \
                   'pg_size_pretty(db_use), pg_size_pretty(db_quota), pg_size_pretty(db_size) ' \
                   'FROM users LEFT JOIN campaigns ON users.id = campaigns.user_id ' \
                   'WHERE user_name = \'%s\'' % config.userName)
    campaignsList = cursor.fetchall()
    cursor.execute('SELECT DISTINCT campaign_id FROM administration.authorizations ' \
                   'WHERE authorized_id IN ' \
                   '(SELECT group_id FROM administration.group_members WHERE ' \
                   'user_id = (SELECT id FROM administration.users WHERE user_name = \'%s\')) ' \
                   'OR authorized_id = (SELECT id FROM administration.users WHERE user_name = \'%s\')' % (config.userName, config.userName))
    authorizedCampaignIdList = [e[0] for e in cursor.fetchall()]
    cursor.connection.commit()
    l = []
    campaignsDict = {}
    for line in campaignsList:
        if not campaignsDict.has_key('%s (%s, db use: %s, quota: %s)' % (line[1], line[0], line[5], line[6])):
            campaignsDict['%s (%s, db use: %s, quota: %s)' % (line[1], line[0], line[5], line[6])] = dict()
        authorization = False
        if line[2] in authorizedCampaignIdList:
            authorization = True
        campaignsDict['%s (%s, db use: %s, quota: %s)' % (line[1], line[0], line[5], line[6])][line[2]] = (line[3], line[4], line[7], authorization)
        l.append(Campaign(line[2], line[3], line[4], line[7], authorization))
    return l

def getCampaignByTitle(title):

    r = getCampaigns()

    for c in r:
        if c.title == title:
            return c

    return None
