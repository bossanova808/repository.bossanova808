################################################################################
# send a JSON command to XBMC and log the human description, json string, and
# the result returned

def sendXBMCJSON (humanDescription, jsonstr):
     Logger.log(humanDescription + " [" + jsonstr +"]")
     result = xbmc.executeJSONRPC(jsonstr)
     Logger.log("JSON result: "  + str(result))

##############################################################################
# helper function - convert player seconds to summat nice for screen 00:00 etc

def getInHMS(seconds):
    hours = seconds / 3600
    seconds -= 3600*hours
    minutes = seconds / 60
    seconds -= 60*minutes
    if hours == 0:
        return "%02d:%02d" % (minutes, seconds)
    return "%02d:%02d:%02d" % (hours, minutes, seconds)

##############################################################################
#unquote text coming back from LMS
def unquoteUni(text):

    try:
        import urllib.parse
        return urllib.parse.unquote(text, encoding=self.charset)
    except ImportError:
        #import urllib
        #return urllib.unquote(text)
        _hexdig = '0123456789ABCDEFabcdef'
        _hextochr = dict((a+b, chr(int(a+b,16))) for a in _hexdig for b in _hexdig)
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        res = text.split('%')
        for i in xrange(1, len(res)):
            item = res[i]
            try:
                res[i] = _hextochr[item[:2]] + item[2:]
            except KeyError:
                res[i] = '%' + item
            except UnicodeDecodeError:
                res[i] = unichr(int(item[:2], 16)) + item[2:]
        return "".join(res)
