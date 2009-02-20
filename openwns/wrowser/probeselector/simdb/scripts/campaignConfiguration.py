#! /usr/bin/python

from pywns.simdb.Parameters import AutoSimulationParameters, Parameters, Bool, Int, Float, String

###########################################
# Please read & delete what you don't need!
###########################################

###################################
# Simple parameter generation HowTo
#
# First, you need to define your simulation parameters in a class derived from Parameters, e.g.
#
class Set(Parameters):
    example = Int()
#
# Then, an instance of Set needs to be created
#

params = Set()

#
# now the Parameters in params get populated with different values. Each time "write" is called the current values fixed.
#

for i in xrange(5):
    params.example = 10**(i)
    params.write()

#
# in your config.py, you need
#

from SimConfig import params

#
# and then configure using the params instance
#

MyExample.examples = params.example

# That's it
####################################

#####################################
# Advanced parameter generation HowTo

#
# Ok, now it gets tricky. First some example from practice:
# Assume you have a given scenario, and you want to evaluate the saturation throughput, depending on
# the number of mobile nodes and the number of subchannels. What would you do with the simple approach?
#

class Set(Parameters):
    numMobileNodes = Int()
    numSubchannels = Int()
    offeredTraffic = Float()

params = Set()

for params.numMobileNodes in [50, 100, 150]:
    for params.numSubchannels in [3, 4, 5]:
        for ot in xrange(1,11):
            params.offeredTraffic = ot*1e6
            params.write()

#
# This creates 3*3*10 = 90 simulations, thus 10 samples for each setting of parameters. And now you hope that
# you have found, for each parameter, some samples below and some above the saturation point. How realistic is that?
# Not very much. So you run all simulations, wait for the output, look at the offered vs. throughput, generate new
# simulations etc... it can be much simpler!
#
# First some definitions:
#  parameter: Something that descibes the type of the scenario, e.g.. numMobileNodes, numSubchannels
#  input: You feed this to your scenario, e.g. offeredTraffic
#  output: Your get this out of your scenario, e.g. throughput
#
# Thus, scenario is a (black-box) function f_{parameter}(input) = output and you search for
#      max_x f_{parameter}(x) = x
# i.e. the highest input so that the output==input. Aka fixed point.
#
# You can do that in the following way:
#
# First, define parameters (with range!) and input (with start value!)
class Set(AutoSimulationParameters):
    # parameters with range
    numMobileNodes = Int(parameterRange = [50, 100, 150])
    numSubchannels = Int(parameterRange = [3, 4, 5])

    # input with start value
    offeredTraffic = Float(default = 1e6)

#
# Then, there needs to be a method which searches through the database and returns a list with entries [scenario_id, value input, value output], given
# a sql-string describing the current parameters, the name of the input variable and a cursor to the db (easy to get, see below)
#
def getTotalThroughput(paramsString, inputName, cursor):

    # query the aggregated ip-throughput of node 1
    myQuery = " \
    SELECT parameter.scenario_id, parameter." + inputName + ", values.mean \
    FROM pd_fs values, (SELECT scenario_id, " + inputName + " FROM parameter_sets WHERE " + paramsString + ") AS parameter \
    WHERE values.scenario_id = parameter.scenario_id AND \
          value.alt_name = 'ip.endToEnd.window.aggregated.bitThroughput_wns.node.Node.id1_SC1' \
    ORDER BY parameter." + inputName + ";"
    cursor.execute(myQuery)
    qResults = cursor.fetchall()

    return qResults

#
# Then, some pre-work to get the cursor
#
conf = config.Configuration()
conf.read("./.campaign.conf")
db.Database.connectConf(conf)
cursor = db.Database.getCursor()

#
# Let the fun start!
# For the initialization, params needs to have the name of the input variable (same as above), the cursor, the campaign id (easy) and a function pointer
# how to get the results
params = Set('offeredTraffic', cursor, conf.parser.getint("Campaign", "id"), getTotalThroughput)

#
# Start a binary search to find the maximum fixed point of the input variable
# maxError is the maximum deviation of input and output to be still "similar" enough, i.e. if (output/input > 1-maxError) then output == input.
#      Required because simulation results fluctuate if not run for an infinite time.
# exactness is the allowed deviation of the fixed point in percent
#      Required because it needs too many samples to find the exact max_x: f(x)=x
# createSimulations = False is a dry run, without writing into the db
# debug is for helpful debug output

[status, results] = params.binarySearch(maxError = 0.1, exactness = 0.05, createSimulations=True, debug=True)
print "%d new / %d waiting / %d finished simulations" %(status['new'], status['waiting'], status['finished'])

#
# if new simulations have been generated -> create scenarios & queue them!
if(status['new'] > 0):
    subprocess.call(['./simcontrol.py --create-scenarios'], shell = True)
    subprocess.call(['./simcontrol.py --queue-scenarios-with-state=NotQueued'], shell = True)
#
# save results
if(status['finished'] > 0):
    outFile = open("currentResults.pkl", "wb")
    pickle.dump(results, outFile)
    outFile.close()

# That's it
# Saves you approx. 70-90% of simulations (time, disk space) in comparison to the simple method
###############################################################################################

