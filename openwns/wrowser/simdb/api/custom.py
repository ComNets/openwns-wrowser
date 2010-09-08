import openwns.wrowser.simdb.Database as db
import openwns.wrowser.Configuration
import psycopg2

def query(sql, campaign=None):

    config = openwns.wrowser.Configuration.Configuration()
    config.read()

    db.Database.connectConf(config)
    cursor = db.Database.getCursor()

    if campaign is not None:
        try:
            createView = "select administration.create_parameter_sets_view(%i);" % campaign.campaignID
            cursor.execute(createView)
            cursor.fetchall()
        except psycopg2.ProgrammingError:
            cursor.connection.commit()

    try:
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        cursor.connection.commit()
    
    return None


