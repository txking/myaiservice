#!/usr/bin/env python

import urllib
import json
import os
import urllib.request


from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

    
def makeWebhookResult(req):
    if req.get("result").get("action") == "shipping.cost":
        result = req.get("result")
        parameters = result.get("parameters")
        zone = parameters.get("shipping-zone")
        cost = {'Europe':100, 'North America':200, 'South America':300, 'Asia':400, 'Africa':500}
        speech = "The APPROXIMATE cost of shipping to " + zone + " is " + str(cost[zone]) + " euros."
        print("Response:")
        print(speech)
        return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "apiai-onlinestore-shipping"
        }
    elif req.get("result").get("action") == "zoho.getloaninfo":
        print("Invoked zoho.getloaninfo")
        result = req.get("result")
        parameters = result.get("parameters")
        loanno = parameters.get("LoanNo")    
        zohourl = "https://creator.zoho.com/api/xml/loaninfo/view/values_Report?authtoken=e22a32c53525cdf5af604978a70a5c4a&zc_ownername=grajesh2000&criteria=(LoanNo%20%3D%3D%20" + loanno + ")"
        print ('LoanNo is {0}, and URL is {1}'.format(loanno, zohourl))
        sres = urllib.request.urlopen(zohourl).read()
        sstr = sres.decode("utf-8")
        # sstr  = sstr[28:-1]
        # speech = json.dumps(sstr, indent=4, sort_keys=True)
        speech = sstr
        print("Response:")
        print(speech)
        return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "zoho-creator-loaninfo"
        }	
    else:
        return {}
	


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    #print "Starting app on port %d" % port
    app.run(debug=True, port=port, host='0.0.0.0')
