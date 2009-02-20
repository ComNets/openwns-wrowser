import os

import pywns.simdb.Parameters

params = pywns.simdb.Parameters.Parameters()
params.read(int(os.path.basename(os.getcwd())))

