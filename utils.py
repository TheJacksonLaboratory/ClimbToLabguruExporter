#!/usr/env/bin python

# lower level utilities to interact with Climb

from logging import NullHandler
import requests
import sys
import json
import datetime
import logging



def getToken(tokenUrl, username, password):

    """ Get the token that the other methods here require. """
    
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

    """
    
    Get samples from Climb.

    Parameters:
    
        endpointUrl (str): Climb's endpoint URL .
        
        myToken (str): The token returned by a call to getToken
        

        Keyword Arguments:
        
            PageSize (int): Number of desired samples per page
            
            PageNumber (int): Which page number the call begins on
            
            all_response (bool): If true, function returns the entire response
                from Climb.
            
    Returns:
    
        samples (list) : A list of dicts, where each dict is a sample
        
        Note: if the all_response keyword arg is set, method instead returns the
            entire response in JSON format.
    
    """

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
    return success        
        

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

