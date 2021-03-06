import itertools

from flask import json

import flyscanner
from flyscanner import return_grid


def get_connections(event_city, event_country, start_city, start_country, out_time, in_time):
    outairports = []
    destairports = []
    airports = json.loads(flyscanner.get_airports(event_city))
    for airport in airports['Places']:
        if str(airport['CountryName']).lower() == str(event_country).lower() and str(
                airport['PlaceName']).lower() == str(event_city).lower():
            destairports.append(airport)
    airports = json.loads(flyscanner.get_airports(start_city))
    for airport in airports['Places']:
        if str(airport['CountryName']).lower() == str(start_country).lower() and str(
                airport['PlaceName']).lower() == str(start_city).lower():
            outairports.append(airport)

    connections = []
    for start in outairports:
        for dest in destairports:
            connections.append(
                json.loads(return_grid(flyscanner.market, flyscanner.currency, flyscanner.locale, start['PlaceId'],
                            dest['PlaceId'],
                            out_time, in_time)))

    for conn in connections:
        conn = conn
        carriers = conn['Carriers']
        dates = conn['Dates']
        currencies = conn['Currencies']
        places = conn['Places']
    output = {'flights': {}}
    i = 0
    d = []
    for date in dates[0]:
        if date is not None:
            d.append(date)
    for inbound in dates[1:]:
        for d1, d2 in itertools.izip(d, inbound[1:]):
            if d2 is None or d1 is None or inbound[0] is None:
                continue
            i += 1
            output['flights'][i] = {"Out": d1['DateString'], "In": inbound[0]['DateString'], "Price": d2['MinPrice'],
                                    "QuoteDateTime": d2['QuoteDateTime']}


    byprice = []
    for flight in output['flights']:
        byprice.append(output['flights'][flight])

    byprice.sort(key=lambda tup: tup['Price'])

    #output['places'] = places

    cheapest = byprice[:4]
    #find hotels:
    for flight in cheapest:
        print flight
        flight['hotel'] = json.loads(flyscanner.get_hotels(event_city, flight['Out'], flight['In'], 1, 1))

    return json.dumps(cheapest)
