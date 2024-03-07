#!/usr/env/bin python

# A high level API to get samples from Climb

from collections import defaultdict
import configparser
import logging
import os
import sys

import utils

class ClimbSamples:

    def __init__(self):
    
        """ Read config file, initialize data members. """
        
        # Load config file, which is in the same directory as the source code.
        config = configparser.ConfigParser()
        src_dir = os.path.dirname(os.path.abspath(__file__))
        config.read(os.path.join(src_dir, "config.cfg"))
        
        # Get the filename containing the password and read it. It is also in the
        # same directory as the code.
        password_filename = os.path.join(src_dir, config["climb"]["password_file"])
        try:
            with open(password_filename) as f:
                self.password = f.read().rstrip()
        except Exception as e:
            err_msg = "Cannot read climb password file " + password_filename
            err_msg += ". Received exception " + str(e)
            sys.exit(err_msg)

        self.endpoint_url =  config["climb"]["endpoint_url"]     
        self.get_token_url = config["climb"]["get_token_url"]
        self.page_size = int(config["climb"]["page_size"])
        self.username = config["climb"]["username"]
        
        # To get samples from more than one Climb instance, we use multiple workgroup_names
        self.workgroup_names = [x.strip() for x in config["climb"]["workgroup_names"].split(',')]
        
        
    def get_samples(self):
    
        """
        
        Get all samples from Climb.
        
        Parameters: None
        
        Returns:
            samples (list): A list of dicts, where each dict represents one sample
            
        """
        
        
        all_samples = []
        token = utils.getToken(self.get_token_url, username=self.username, password=self.password)
         
        for workgroup_name in self.workgroup_names:
            # Get the first token, set the workgroup, get the 2nd token, and THEN the samples
            if (utils.setWorkgroup(self.endpoint_url, token, workgroup_name)):
                token2 = utils.getToken(self.get_token_url, username=self.username, password=self.password)
            else:
                logging.error(f"Couldn't set workgroup and get token for workgroup {workgroup_name}")
                continue
                
            # We can't get all the samples from Climb at once due to the PageSize limit. Instead, we have to make successive
            # calls, incrementing the PageNumber each time, until we get fewer samples than the page size, which is set
            # in the config file.
            page_number=1
            logging.info(f"Getting climb samples for workgroup {workgroup_name}...")
            samples = []
            while True:
                curr_samples = utils.getSamples(self.endpoint_url, token2, all_response=True, PageSize=self.page_size,
                    PageNumber=page_number).get("data").get("items")
                samples += curr_samples
                if len(curr_samples) < self.page_size:
                    # Stop when we find fewer samples than the page size.
                    logging.info(f"Found {len(samples)} samples in Climb.")
                    all_samples += samples
                    break
                page_number += 1
        return all_samples
                

if __name__ == "__main__":

    # Run by itself, this code just prints out a count of each sample type.

    # Get all the samples
    climb_samples = ClimbSamples()
    samples = climb_samples.get_samples()
    print(f"Found {len(samples)} total samples.")
    
    # Create the histogram countiung each sample type.
    # Also track the names
    all_names = defaultdict(set)
    type_histogram = defaultdict(int)
    id_counter = defaultdict(set)
    for sample in samples:
        type_histogram[sample['type']] +=1
        id_counter[sample['type']].add(sample['sampleID'])
        all_names[sample['type']].add(sample['name'])
        
    # Print the histrogram
    sorted_keys = sorted(type_histogram.keys())
    for sample_type in sorted_keys:
        #type_count = type_histogram[sample_type]
        #id_count = len(id_counter[sample_type])
        #print(f"{sample_type}: {type_count}, id_count: {id_count}")
        
        if sample_type == "Serum":
            print(f"Serum: {len(all_names['Serum'])} samples.")
            print(f"{sorted(all_names[sample_type])}")
        # Print all the sample IDs as a comma-delimited string
        #sample_ids = ','.join(id_counter[sample_type])
        #print(sample_ids)
        
        
        
        