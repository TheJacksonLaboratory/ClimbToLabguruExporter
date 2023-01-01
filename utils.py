from logging import NullHandler
import requests
import sys
import json
import datetime
import logging

tokenUrl = 'http://climb-admin.azurewebsites.net/api/token'
endpointUrl = 'https://api.climb.bio/api/'

#username = your-climb-acct-name
#password = your-climb-account-password

# Global for convenience
myToken = None

def getToken(tokenUrl, username, password):
    try:
        """ Given a username and password, return an access token good for an hour."""
        response = requests.get(tokenUrl,auth=(username,password))
        myContent = response.json()
        global myToken
        myToken = myContent['access_token']
        return myToken
    except requests.exceptions.Timeout as e: 
        print(e)
        raise Exception(e)
    except requests.exceptions.InvalidHeader as e: 
        print("Invalid Header")
        print(e)
        raise ValueError(e)
    except requests.exceptions.InvalidURL as e:  
        print("Invalid Url")
        print(e)
        raise ValueError(e)
    except requests.exceptions.RequestException as e:  # All other request exceptions
        print("general request exception")
        print(str(e))
        raise SystemExit(e)
        
    except Exception as e:
        print("general error")
        print(str(e))
        raise SystemExit(e)


def getSamples(endpointUrl, myToken, **kwargs):
    try:
        call_header = {'Authorization' : 'Bearer ' + myToken}
        wgResponse = requests.get(endpointUrl+'samples', headers=call_header, params=kwargs)
        wgJson = wgResponse.json()
        # If caller passed the all_response argument, give the whole thing
        if kwargs.get("all_response"):
            return wgJson
        # Check for number of items
        total_item_count = wgJson.get('totalItemCount')
        outer_dict = wgJson.get('data')
        # Get a list of samples, where each sample is a dict
        item_list = outer_dict.get('items')
        return item_list
    except requests.exceptions.Timeout as e: 
        print(e)
        raise Exception(e)
    except requests.exceptions.InvalidHeader as e:  
        print(e)
        raise ValueError(e)
    except requests.exceptions.InvalidURL as e:  
        print(e)
        raise ValueError(e)
    except requests.exceptions.RequestException as e:  # All others
        print(e)
        raise SystemExit(e)

                
def getWorkgroups(endpointUrl, myToken):
    try:
        call_header = {'Authorization' : 'Bearer ' + myToken}
        wgResponse = requests.get(endpointUrl+'workgroups', headers=call_header)
        wgJson = wgResponse.json()
        # Check for number of items
        total_item_count = wgJson.get('totalItemCount')
        outer_dict = wgJson.get('data')
        # Get a list of workgroups where each group is a dictionary
        dict_list = outer_dict.get('items')
        return dict_list
    except requests.exceptions.Timeout as e: 
        print(e)
        raise Exception(e)
    except requests.exceptions.InvalidHeader as e:  
        print(e)
        raise ValueError(e)
    except requests.exceptions.InvalidURL as e:  
        print(e)
        raise ValueError(e)
    except requests.exceptions.RequestException as e:  # All others
        print(e)
        raise SystemExit(e)

        
# Workgroup name example: 'KOMP AI Training'
def setWorkgroup(endpointUrl, myToken, workgroupName):
    dict_list = getWorkgroups(endpointUrl, myToken)
    success = False

    for x in dict_list:
        if x['workgroupName'] == workgroupName:
            call_header = {'Authorization' : 'Bearer ' + myToken}
            status_code = requests.put(endpointUrl+'workgroups/'+str(x['workgroupKey']), headers=call_header)
            print(status_code)
            success = True

    # If successful, remember to get a new access token!
    if success == False:
        print(f'"Could not change workgroup to {workgroupName}')
        raise SystemExit(f'"Could not change workgroup to {workgroupName}')
        
        
"""
Data package:
{
  "genotypeRequestDtos": [
    {
      "animalID": 0,
      "plateKey": null,
      "genotypes": [
        {
          "date": "string",
          "genotypeAssayKey": 0,
          "genotypeSymbolKey": 0
        }
      ]
    }
  ]
}
"""
# POST example for genotypes
def postGenotype(endpointUrl, myToken, animalId,genotypeAssayKey, genotypeSymbolKey):
    try:
        # Construct the data payload inside out
        complete_date = datetime.datetime.now()
        date_str = '{:%Y%m%d}'.format(complete_date)
        
        genotype_dict = { "date" : date_str, "genotypeAssayKey" : genotypeAssayKey, "genotypeSymbolKey" : genotypeSymbolKey }
        genotype_ls = [ genotype_dict ]

        genotypeRequestDto_dict = { "animalID" : animalId, "plateKey" : None, "genotypes" : genotype_ls}

        genotypeRequestDtos_ls = [genotypeRequestDto_dict]
        genotypeRequestDtos_dict = { "genotypeRequestDtos" : genotypeRequestDtos_ls}

        api_call_headers = {"Content-type" : "application/json;", "Authorization": "Bearer " + myToken}

        print(json.dumps(genotypeRequestDtos_dict))
        r = requests.post(endpointUrl + 'genotypes', data=json.dumps(genotypeRequestDtos_dict), verify=True, allow_redirects=False, headers=api_call_headers)
        print("RESULT:" + r.text)
        return r.status_code
    except requests.exceptions.Timeout as e: 
        print(e)
        raise Exception(e)
    except requests.exceptions.InvalidHeader as e:  
        print(e)
        raise ValueError(e)
    except requests.exceptions.InvalidURL as e:  
        print(e)
        raise ValueError(e)
    except requests.exceptions.RequestException as e:  # All others
        print(e)
        raise SystemExit(e)

"""
Data package
{
  "animalID": 0,
  "plateKey": null,
  "date": "string",
  "genotypeAssayKey": 0,
  "genotypeSymbolKey": 0
}
"""
# PUT example for genotypes
def putGenotype(endpointUrl, myToken, animalId, genotypekey, genotypeAssayKey, genotypeSymbolKey):
    try:
        print(f'PUTTING genotypeAssayKey {genotypeAssayKey} and symbol key {genotypeSymbolKey} genotype for { animalId } and genotypeKey {genotypekey}.')
        # Construct the data payload inside out
        complete_date = datetime.datetime.now()
        date_str = '{:%Y%m%d}'.format(complete_date)
        
        genotype_dict = { "animalID" : animalId, "plateKey" : None, "date" : date_str, "genotypeAssayKey" : genotypeAssayKey, "genotypeSymbolKey" : genotypeSymbolKey }
        
        api_call_headers = {"Content-type" : "application/json;", "Authorization": "Bearer " + myToken}

        print(json.dumps(genotype_dict))
        
        r = requests.put(endpointUrl + 'genotypes/'+ str(genotypekey), data=json.dumps(genotype_dict), headers=api_call_headers)
        print("RESULT:" + r.text)
        
    except requests.exceptions.Timeout as e: 
        print(e)
        raise Exception(e)
    except requests.exceptions.InvalidHeader as e:  
        print(e)
        raise ValueError(e)
    except requests.exceptions.InvalidURL as e:  
        print(e)
        raise ValueError(e)
    except requests.exceptions.RequestException as e:  # All others
        print(e)
        raise SystemExit(e)

