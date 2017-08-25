#!/usr/bin/env python

import urllib
import json
import os
import urllib.request
import xml.dom.minidom
import requests
import json

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
        
        # handle XML
        dxml = xml.dom.minidom.parseString(sstr) 
        sstr = dxml.toprettyxml()
        
        # handle JSON
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
	
def analyze(text, username, password):
    anger = list()
    fear = list()
    disgust = list()
    joy = list()
    sadness = list()
    
    json_output = analyze_single(text, username, password)
    anger.append(json_output['document_tone']['tone_categories'][0]['tones'][0]['score'])
    fear.append(json_output['document_tone']['tone_categories'][0]['tones'][1]['score'])
    disgust.append(json_output['document_tone']['tone_categories'][0]['tones'][2]['score'])
    joy.append(json_output['document_tone']['tone_categories'][0]['tones'][3]['score'])
    sadness.append(json_output['document_tone']['tone_categories'][0]['tones'][4]['score'])

    lsret = "Overview of average emotional levels (0 <= n <= 1) \n"

    lsret = lsret + 'Anger: ' + str(sum(anger) / len(anger))) + '\n'
    lsret = lsret + ' '.join(anger) + '\n'
    lsret = lsret + 'Fear: ' + str(sum(fear) / len(fear))) + '\n'
    lsret = lsret + ' '.join(fear) + '\n'
    lsret = lsret + 'Disgust: ' + str(sum(disgust) / len(disgust))) + '\n'
    lsret = lsret + ' '.join(disgust) + '\n'
    lsret = lsret + 'Joy: ' + str(sum(joy) / len(joy))) + '\n'
    lsret = lsret + ' '.join(joy) + '\n'
    lsret = lsret + 'Sadness: ' + str(sum(sadness) / len(sadness))) + '\n'
    lsret = lsret + ' '.join(sadness) + '\n'

    print (lsret)
    return lsret


# Returns the json for analysis of a single string of any length
def analyze_single(text, username, password):
    url = "https://gateway.watsonplatform.net/tone-analyzer-beta/api/v3/tone?version=2016-02-11&tones=emotion&sentences=false&text=" + urllib.parse.quote(text.encode('utf-8'))
    try:
        req = requests.get(url, auth=(username, password))
    except:
        return '{Error calling Watson}'
    return req.json()
        
        
def format_tone_json(data):
    data = json.loads(str(data))
    print(data)
    lsret = 'FNM Buddy Tone Analysis results : \n' 
    for i in data['document_tone']['tone_categories']:
        lsret = lsret + i['category_name'] + '\n'
        lshypens = "-" * len(i['category_name'])
        lsret = lsret + lshypens + '\n'
        for j in i['tones']:
            lsret = lsret + j['tone_name'].ljust(20) + (str(round(j['score'] * 100,1)) + "%").rjust(10) + '\n'
        print(lsret)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    #print "Starting app on port %d" % port
    app.run(debug=True, port=port, host='0.0.0.0')
