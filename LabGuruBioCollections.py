#!/usr/env/bin/python

# An interface for querying and updating our custom inventory
# collections in LabGuru

from collections import defaultdict
import configparser
import json
import logging
import requests
import os
import sys
import urllib


class LabGuruBioCollections:

    """ Query and update our custom inventory collections in LabGuru """

    def __init__(self):

        """ Parse config file, read tokens. """
        
	    # Load config file, which is in the same directory as the source code.
        self.config = configparser.ConfigParser()
        src_dir = os.path.dirname(os.path.abspath(__file__))
        self.config.read(os.path.join(src_dir, "tail_only_config.cfg"))
		
        self.request_headers = { 'accept': 'application/json',
            'Content-Type': 'application/json' }
            
        # Get the filename containing the token and read it
        token_filename = self.config["credentials"]["labguru_token_file"]
        try:
            with open(token_filename) as f:
                self.token = f.read().rstrip()
        except Exception as e:
            err_msg = "Cannot read labguru token file " + token_filename
            err_msg += ". Received exception " + str(e)
            sys.exit(err_msg)
        
        # Get shortcuts to the urls for updating sample collections
        self.sample_descriptions = self.config["labguru_sample_descriptions"]
        self.sample_urls = self.config["labguru_api_sample_urls"]
        self.base_url = self.sample_urls["base_url"]
        
        # We need to keep track of what samples are already in Labguru so that we don't add a sample
        # again. We also need to know which sample names have duplicate entries (i.e., samples with the same
        # name. Unfortunately, the system has no way to do that, so we query it and make a lookup table.
        # Our table is a dict, where each key is a sample_type, and each value is a dict, where the keys are
        # each existing samples of that type, and the values are the count of how many times that sample name
        # was found.
        self.existing_samples = {}
        self.__load_existing_samples()


    def add_sample(self, sample_type, sample_name):
    
        """
        
        Add a sample into Labguru.

        Parameters:
        
            sample_type (str): The sample's type.
            
            sample_name (str): The samples' name.
            
        Returns:
        
            Bool : True if added, false if not.
        
        """

        if self.__skip_samples(sample_type):
            logging.debug(f"Skipping sample {sample_name} due to skipped type {sample_type}")
            return False
            
        if self.sample_exists(sample_type, sample_name):
            logging.debug(f"Sample {sample_name} of type {sample_type} already exists, skipping.")
            return False
            
        url = self.get_url(sample_type)
        desc = self.get_description(sample_type)
        
        payload = { "token" : self.token,
            "item": {
                "name": sample_name,
                "description": desc
            }
        }
        logging.debug(f"Attempting to add sample {sample_name} of type {sample_type}...")
        response = requests.request("POST", url, headers=self.request_headers,
            json = payload).text.encode('utf-8').decode("utf-8")
        
        # A successful request should return a json dict. Confirm it contains a valid auto_name
        # generated by LabGuru for the new sample.
        try:
            auto_name = json.loads(response)["auto_name"]
            logging.info(f"Successfully added sample {sample_name} of type {sample_type}.")
        except Exception:
            logging.error(f"Could not add sample {sample_name} of type {sample_type}. Response: {response}")

        
    def get_description(self, sample_type):
    
        """ Get the description to be added to the sample. """
            
        if self.__skip_samples(sample_type):
            logging.debug(f"Skipping sample of type {sample_type}.")
            return None
           
        short_type = self.__get_short_type(sample_type)
        desc = self.sample_descriptions[short_type]
        # There some special cases. This handling is a hack but will suffice.
        if short_type == "Kidney":
            if "Left" in sample_type:
                desc = "Left Kidney"
            elif "Right" in sample_type:
                desc = "Right Kidney"
            else:
                logging.error(f"Cannot get description for Kidney sample {sample_type}")
        return desc


    def get_url(self, sample_type):
    
        """ Get the custom collection URL for adding samples of the given type. """
        
        # Determine whether we should skip this kind of sample
        if self.__skip_samples(sample_type):
            logging.debug(f"Skipping sample of type {sample_type}.")
            return None
        url = None
        short_type = self.__get_short_type(sample_type)
        try:
            url = self.base_url + self.sample_urls[short_type]
        except KeyError:
            logging.error(f"Sample type {sample_type} not found in sample collections")
        
        # Change spaces to '%20'
        url = url.replace(' ', '%20')
        return url
	
    def sample_exists(self, sample_type, sample_name):
    
        """ Find whether this sample already exists in LabGuru. """

        # All existing samples were indexed by their short_type.
        short_type = self.__get_short_type(sample_type)
        val = sample_name in self.existing_samples[short_type]
        return val
        
    def show_duplicates(self):
    
        """ For all collections, print duplicate samples and dup counts. """
        
        total_dups = 0
        for short_type, name_counts in self.existing_samples.items():
            type_dups = 0
            logging.info(f"\n\nFor sample type {short_type}:")
            for sample_name, count in name_counts.items():
                if count > 1:
                    logging.debug(f"Sample {sample_name} occurs {count} times.")
                    type_dups += 1
            logging.info(f"Sample type {short_type} has {type_dups} duplicated samples.")
            total_dups += type_dups
        logging.info(f"\n\nThere were {total_dups} duplicated samples.")

    def __get_short_type(self, sample_type):
    
        """ Get the lowercase first word from the sample with no hyphens."""
        
        short_type = sample_type.replace('-', ' ').split(' ')[0].lower()
        return short_type
        
    def __load_existing_samples(self):
    
        """ Find and store the names of all samples already in Labguru. """
        
        payload = { "token" : self.token, "page_size": 2500}
        
        # For each kind of sample, get a list of existing samples.
        for short_type, url in self.sample_urls.items():
            if short_type == "base_url":
                continue
            full_url = (self.base_url + url).replace(' ', '%20')
 
            response = requests.request("GET", full_url, headers=self.request_headers,
                json=payload).text.encode('utf-8').decode("utf-8")
            try:
                samples = json.loads(response)
            except Exception as e:
                logging.error(f"Could not load response for {short_type} as json. Received exception {str(e)}. Url was {url}")
                continue
        
            # Make a dict of samples. Keys are names, vals are number of times that name occurred.
            sample_names = defaultdict(int)
            for sample in samples:
                if type(sample) is dict:
                    logging.debug(f"{sample}\n")
                    # We want to track which samples are duplicates that must be deleted.
                    self.__track_duplicates(short_type, sample)
                    sample_names[sample["name"]] +=1
                else:
                    logging.error(f"For {short_type}, found non-dict sample {sample}.")
                
            logging.debug(f"For sample_type {short_type}, found samples: {sample_names}")
            self.existing_samples[short_type] = sample_names
        
        
    def __skip_samples(self, sample_type):
    
        """ Determine whether given sample type should be skipped. """
        
        return sample_type in self.config["skip_samples"]
    
    
    def __track_duplicates(self, short_type, sample):
    
        """ Keep oldest sample, mark any with same name for deletion. """
        
        sample_name = sample["name"]
        curr_id = sample['id']
        curr_create_time = sample['created_at']
        
        # If we don't yet have this short type or sample in our tracker, insert it as a key, where the
        # val is a dict with the id and 'created_at' time.
        if short_type not in self._sample_tracker or sample_name not in self._sample_tracker[short_type]:
        
            self._sample_tracker[short_type][sample_name] = { 'id' : curr_id, 'created_at' = curr_create_time }
            return
            
        # If we already have this sample, and the new one's created_at time is greater than or equal to the
        # old one's, then put the new one's id on the deletion list. O/w, put thbe new one's id and created_at
        # time in the tracker, and put the old one's id on the deletion list.
        prev_id = self._sample_tracker[short_type][sample_name]['id']
        prev_create_time = self._sample_tracker[short_type][sample_name]['created_at']
        
        if curr_create_time < prev_create_time:
            # Current sample is older. Put it in the tracker, and mark the one that was there for deletion.
            self._sample_tracker[short_type][sample_name]['id'] = curr_id
            self._sample_tracker[short_type][sample_name]['created_at'] = curr_create_time
            self._dups_to_delete.append(prev_id)
        
        else:
            # Current sample is not older. Leave the sample in the tracker unchanged, and mark the
            # current one for deletion.
            self._dups_to_delete.append(curr_id)
            
        
            
        
        
    
    
if __name__ == "__main__":
    lgbc = LabGuruBioCollections()
	
		
