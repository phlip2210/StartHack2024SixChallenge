"""
An example interface designed to be imported in your projects as a library.
"""
import urllib.request
import ssl
import json
from typing import List, Dict, Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from kafe2 import XYContainer, Fit, Plot, XYFit, MultiFit
#from uncertainties import ufloat

class APIError(Exception):
    def __init__(self, message: str, correlation_id: str = None):
        self.message = message
        self.correlation_id = correlation_id
        super().__init__(message)


class FinancialDataAPI:
    def __init__(self, certificate_path: str):
        self.url = 'https://web.api.six-group.com/api/findata'
        self.headers = {
            "accept": "application/json"
        }
        self.context = ssl.SSLContext()
        self.context.load_cert_chain(f'{certificate_path}/signed-certificate.pem', f'{certificate_path}/private-key.pem')

    def _http_request(self, end_point: str, query_string: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make an HTTP request and send the raw response.
        """
        complete_url = f"{self.url}{end_point}?{urllib.parse.urlencode(query_string)}"
        try:
            request = urllib.request.Request(complete_url, headers=self.headers)
            with urllib.request.urlopen(request, context=self.context) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as err:
            correlation_id = err.headers.get('X-CorrelationID')
            raise APIError("An error occurred during the API request.", correlation_id) from err

    def _http_request_with_scheme_id(self, end_point: str, scheme: str, ids: List[str]) -> Dict[str, Any]:
        """
        Make an HTTP request using scheme and ids.
        """
        query_string = {
            'scheme': scheme,
            'ids': ",".join(ids)
        }
        return self._http_request(end_point, query_string)

    def instrumentBase(self, scheme: str, instruments: List[str]) -> Dict[str, Any]:
        """
        Retrieve instrument basic attributes using scheme and ids.
        """
        end_point = "/v1/instruments/referenceData/instrumentBase"  # instruments
        return self._http_request_with_scheme_id(end_point, scheme, instruments)

    def endOfDayHistory(self, scheme: str, listings: List[str], dateFrom: str, dateTo: str = '') -> Dict[str, Any]:
        """
        Retrieve End of Day Timeseries data.
        """
        end_point = "/v1/listings/marketData/endOfDayHistory"
        query_string = {
            'scheme': scheme,
            'ids': ",".join(listings),
            'dateFrom': dateFrom,
            'dateTo': dateTo
        }
        return self._http_request(end_point, query_string)
    
all_activities = ['EET Data Set Information', 'Main criterias used for a first screening of ESG related products',
               'Manufacturer commitment to responsible investment', 'Manufacturer Engagement & Stewardship Activities', 'Carbon Emissions & Paris Agreement', 'ESG thematic investing description', 'Financial_Instrument ESG Benchmark', 
               'MiFID/IDD Target Market - Manufacturer angle (from a client perspective)', 'Minimum (or planned) Sustainable investment and taxonomy assets allocation breakdown', 'Scoping according to SFDR annex template', 'Taxonomy aligned investments (for definitions please refer to the RTS)', 
'Greenhouse gas emissions', 'Biodiversity', 'Water', 'Waste', 'Social and employee matters', 'Energy Performance', 'Water, waste and material emissions', 'Green securities', 'Energy efficiency', 'Human rights', 'Anti-corruption and anti-bribery',
 'Environmental', 'Social', 'Governance', 'Fossil fuels', 'Energy consumption', 'Negative Screening / Exclusions', 'Adult entertainment', 'Alcohol', 'Animal_Testing', 'Cannabis', 'Coal', 'Conventional weapons', 'Factory_Farming', 'FUR', 'Gambling', 'Gas', 'Genetic_Engineering', 'GMO', 'Nuclear Energy', 
 'Nuclear weapons', 'Oil', 'Other_Fossil_Fuel (i.e. Tar Sands/Sands...)', 'Norm based exclusions', 'Real Estate screening', 'Palm_Oil', 'Pesticides', 'Research_on_human_embryos', 'Tobacco', 'Unconventional / controversial weapons', 'Sovereign level exclusions', 'French MiFID Market', 'German MiFID Market', 
 'Supplementary Taxonomy Information - V1.1.1 - Gas and Nuclear', 'MiFID Sustainability Preference Flag', 'Last reported Sustainable investment and taxonomy assets allocation breakdown', 'AMF Doctrine', 'Financial_Instrument ESG and Engagement Coverage (Corporate and sovereign)', 'Structured Products Additional Information']
    
cut = ['Manufacturer commitment to responsible investment',  'Carbon Emissions & Paris Agreement',    'Greenhouse gas emissions', 'Biodiversity', 'Water', 'Waste', 'Social and employee matters', 'Energy Performance', 'Water, waste and material emissions', 'Green securities', 'Energy efficiency', 'Human rights', 'Anti-corruption and anti-bribery',  'Environmental', 'Social', 'Governance', 'Fossil fuels', 'Energy consumption','Adult entertainment', 'Alcohol', 'Animal_Testing', 'Cannabis', 'Coal', 'Conventional weapons', 'Factory_Farming', 'FUR', 'Gambling', 'Gas', 'Genetic_Engineering', 'GMO', 'Nuclear Energy', 
 'Nuclear weapons', 'Oil', 'Other_Fossil_Fuel (i.e. Tar Sands/Sands...)',  'Palm_Oil', 'Pesticides', 'Research_on_human_embryos', 'Tobacco', 'Sovereign level exclusions']

user_rating = {'Water': 0.8, 'Environmental': 0.9, 'Oil': -0.1, 'Nuclear weapons': -0.7, 'Coal': -0.5, 'Greenhouse gas emissions': 1.0, 'Biodiversity': 0.8, 'Waste': 0.8}


if __name__ == '__main__':
    
    data = np.array(pd.read_csv('EUESGMANUFACTURER.csv', delimiter= ',', skiprows = 1, decimal = '.'))
    #activities = []
    #bigdict = {}
    average_sized_dict={}
    ISBN = ''
    active_activity = ''
    used_activity = []
    ratio = []
    qsummit = []
    score = 0
    scorenorm = 0
    
    for j in range(len(data[:, 1])):
        if data[j, 15] in user_rating:
            if data[j, 1] != ISBN:

                if len(qsummit) > 0:
                    atze = np.mean(qsummit)
                    score += (1-abs(atze-user_rating[active_activity])/2)*abs(user_rating[active_activity])
                    #print("sc", score)
                    scorenorm += abs(user_rating[active_activity])
                qsummit = []
                #print(data[j, 1])

                #print(activities)
                #bigdict[ISBN] = activities
                for activity in user_rating:
                    #print(activity)
                    if activity not in used_activity and user_rating[activity] < 0 and score != 0:
                        score -= user_rating[activity]
                        scorenorm -= user_rating[activity]
                if scorenorm != 0:
                    average_sized_dict[ISBN] = score/scorenorm
                else:
                    pass
                    #print("ERROR:", score)
                    #average_sized_dict[ISBN] = 0
                score = 0
                scorenorm = 0
                ISBN = data[j, 1]
                active_activity = data[j, 15]
                used_activity = [active_activity]
                #print("\n".join(ratio))
               # ratio = []
            #else:
                #if data[j, 15] not in activities:
                    #activities.append(data[j, 15])
            if active_activity != data[j, 15]:
                if len(qsummit) > 0:
                    atze = np.mean(qsummit)
                    score += (1-abs(atze-user_rating[active_activity])/2)*abs(user_rating[active_activity])
                   # print("sc", score)
                    scorenorm += abs(user_rating[active_activity])
                qsummit = []
                active_activity = data[j, 15]
                used_activity.append(active_activity)
                

            if data[j, 19] == "7 : Ratio":
                    if data[j, 18] != data[j,18]:
                        print(type(data[j, 18]))
                        pass
                    else:
                        atze1 = data[j, 18]
                        #print(atze1)
                        while atze1 > 1:
                            atze1/=10
                        qsummit.append(atze1)
    
    
    sorted_dict = sorted(average_sized_dict.items(), key=lambda x:x[1])
    print(sorted_dict[-3:])
    

    activities = []
    for j in range(len(data[:, 1])):
        if data[j, 1] == sorted_dict[-1][0] and data[j, 15] in user_rating and data[j, 15] not in activities:
            activities.append(data[j, 15])
            num1 = data[j, 2]
    print(activities)
        



    findata = FinancialDataAPI("C:\\Users\marku\OneDrive\Dokumente\StartHack\pemdirectory")

    sample = findata.instrumentBase("ISIN", [num1])
    #sample = findata.endOfDayHistory("ISIN_BC", ["CH1240611561_512"], '2024-01-01')
    #print(sample)
    #
    print(json.dumps(sample, sort_keys=True, indent=5))