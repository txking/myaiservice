#!/usr/bin/env python

import urllib
import json
import os
import urllib.request
import xml.dom.minidom
import json
import pprint

from flask import Flask
from flask import request
from flask import make_response

from googleapiclient.discovery import build


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
        "source": "rajesh-apiai-onlinestore-shipping"
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
        "source": "rajesh-zoho-creator-loaninfo"
        }
    elif req.get("result").get("action") == "zoho.getloaninfojson":
        print("Invoked zoho.getloaninfo")
        result = req.get("result")
        parameters = result.get("parameters")
        loanno = parameters.get("LoanNo")    
        zohourl = "https://creator.zoho.com/api/json/loaninfo/view/values_Report?authtoken=e22a32c53525cdf5af604978a70a5c4a&zc_ownername=grajesh2000&criteria=(LoanNo%20%3D%3D%20" + loanno + ")"
        print ('LoanNo is {0}, and URL is {1}'.format(loanno, zohourl))
        sres = urllib.request.urlopen(zohourl).read()
        sstr = sres.decode("utf-8")
        
        
        # handle JSON
        sstr  = sstr[28:-1]
        speech = json.dumps(sstr, indent=4, sort_keys=True)
               
        
        print("Response:")
        print(speech)
        return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "rajesh-zoho-creator-loaninfojson"
        }		
    elif req.get("result").get("action") == "dobuddy.tonecheck":
        print("Invoked dobuddy.tonecheck")
        result = req.get("result")
        parameters = result.get("parameters")
        tonetext = parameters.get("tonetext")    
        speech = analyze(tonetext)
        return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "rajesh-watson-tone-check"
        }
    elif req.get("result").get("action") == "custom.searchnow":
        print("Invoked custom.searchnow")
        result = req.get("result")
        parameters = result.get("parameters")
        searchtext = parameters.get("searchtext")    
        speech = googlesearch(searchtext)
        return {
        "speech": speech,
        "displayText": speech,
        "data": speech,
        # "contextOut": [],
        "source": "rajesh-fnmsite-search"
        }        
    else:
        return {}


def googlesearch(stext):
    print ("GGGGGGGGGG  Will GOOGLE search  GGGGGGGGGGGGGG")
    service = build("customsearch", "v1",developerKey="AIzaSyAIxk6eBuIuSXotmMN2qabwAy5NoLYnk8Y")

    res = service.cse().list(q=stext,cx='002730420427000960612:0as1dxnsjnq',).execute()
	
	print (res)
    # pprint.pprint(res)
    return res


		
def analyze(text):
    anger = list()
    fear = list()
    disgust = list()
    joy = list()
    sadness = list()

    watsonurl = 'https://watson-api-explorer.mybluemix.net/tone-analyzer/api/v3/tone?text=' + urllib.parse.quote_plus(text) + '&tones=emotion%2Clanguage%2Csocial&sentences=false&version=2016-02-11'
    print (watsonurl)
    json_output = urllib.request.urlopen(watsonurl).read()
    print ('*** JSON OUTPUT ***')
    print (json_output)
    sstr = json_output.decode("utf-8")
    print (sstr)
    lsret = format_tone_json(sstr)
    return lsret

	
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
    return lsret


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    #print "Starting app on port %d" % port
    app.run(debug=True, port=port, host='0.0.0.0')
