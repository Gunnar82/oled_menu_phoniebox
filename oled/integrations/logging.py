import settings


lERROR = 1
lINFO = 2
lDEBUG = 3
lDEBUG2 = 4
lDEBUG3 = 5

loglevel = ["ERROR", "INFO", "DEBUG", "DEBUG2", "DEBUG3"]


def log(ll,logtext):


    if ll > len(loglevel):
        ll = len(loglevel) - 1
    if settings.LOGLEVEL >= ll:
        print ("%s: %s"%(loglevel[ll-1], logtext))