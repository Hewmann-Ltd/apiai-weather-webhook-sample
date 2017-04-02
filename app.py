#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

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

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") == "yahooWeatherForecast":
        baseurl = "https://query.yahooapis.com/v1/public/yql?"
        yql_query = makeYqlQuery(req)
        if yql_query is None:
            return {}
        yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
        result = urlopen(yql_url).read()
        data = json.loads(result)
        res = makeWebhookResult(data)
        return res
    elif req.get("result").get("action") == "where.is":
        result = req.get("result")
        parameters = result.get("parameters")
        location = parameters.get("facility")

        area = {'Toilets':'are located before security, beside Spar in Main Terminal building, or after security, at Gate 30, and Gate 3. We wanted to let you know that we are working hard to create the airport our region loves and are planning some renovations to the upper retail level, located after Security. The upgrades mean that we will have to close the toilets on the upper retail level. The nearest toilets will be on the lower retail level and there will be signage in place.','Arrivals':'in the main terminal building', 'Starbucks':'is located at the check-in area, before security, and in the Departure Lounge, after security on the Lower Level.', 'Spar':'At right hand side of terminal building', 'Lounge':'is located after security on the lower level. The Aspire Premium Lounge at Liverpool John Lennon Airport is open to all passengers regardless of travel class.','Car Hire':'. We offer car hire from Europcar, Hertz, Enterprise and Avis, all of which can be found in Liverpool John Lennon Airport Car Rental Centre, located on the ground floor of the short stay multi-storey car park directly opposite the terminal building, across from the Arrivals Area. Just walk across from the terminal building towards the Express Drop Off & Pick Up Car Park. Cars can be returned to the Car Rental Car Park, located off the airport approach road by taking the third exit off the roundabout.','Security':'Liverpool John Lennon Airport recommends passengers arrive a minimum of 2 hours before departure to allow sufficient time to check-in, pass through airport security and to take advantage of the many new passenger facilities now available in the departure lounge.','Subway':'can be found in the Departure Lounge, after security on the Lower Level. It can also be found on the Arrivals concourse, on the ground floor.','Kissing Gate':'can be found in the Departure Lounge, after security on the Lower Level.','Parking':'Disabled parking spaces are located at the front of the car parks (Long Stay, Fast Track, and Multi-Storey), they are subject to availability.','Parking Fast Track':'The Fast Track Car Park can be accessed by turning left off the dual-carriageway as you approach the terminal building, following green signs for RVP. After half a mile turn right, following signs for Fast Track Car Park.','Parking Long Stay':'The Long Stay and Multi Storey Car Parks can be accessed by turning left on the roundabout when approaching the airport terminal.','Checkin Desks':'at the left hand side of terminal building after you enter.','Short Stay Parking':'Situated undercover away from the elements and directly opposite the terminal building, the Short Stay Car Park is ideal for those picking passengers up, or dropping them off at the airport. This car park also couldn’t be closer to the airport with just a minutes walk to check-in.','Cash Machine':'Beside Travelex in the Upper Level.'}

        speech = "Liverpool John Lennon Airport " + location + " " + str(area[location]) + " . Do you need anything else?"

        print("Response:")
        print(speech)
        
        
          
    else:
        return {}
    
    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "Oblige Global Limited"
    }
    


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + " Airport"  + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " degrees farenheit. Do you need anything elese?"

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "Oblige Global Limited"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
