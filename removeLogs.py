import datetime
import glob
import os,sys
import time
start = time.perf_counter()

TMPDIR = '/tmp/'
REPDIR = '/usr/local/simpaisa/backend/generatereport/logs/'

DAY = 2
x = datetime.datetime.now()
print(x)


DT = datetime.datetime.now() - datetime.timedelta(days = DAY)
#_7DAYAGO   =  DT.strftime('%Y-%m-%d')
_2DAYAGO  =  DT.strftime('%Y%m%d')

tmpFiles = glob.glob(TMPDIR+"*"+_2DAYAGO+"*")
for filename in tmpFiles:
    print("Tmp Removing %s" % (filename),flush=True)
    os.remove(filename)

repFiles = glob.glob(REPDIR+"*"+_2DAYAGO+"*")
for filename in repFiles:
    print("Report logs Removing %s" % (filename),flush=True)
    os.remove(filename)

