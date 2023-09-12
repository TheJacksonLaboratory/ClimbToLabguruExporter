#!/usr/env/bin python

# A high level API to get samples from Climb

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
        self.workgroup_name = config["climb"]["workgroup_name"]
        
        
    def get_samples(self):
    
        """
        
        Get all samples from Climb.
        
        Parameters: None
        
        Returns:
            samples (list): A list of dicts, where each dict represents one sample
            
        """
        
        # Get the first tokeb, set the workgroup, get the 2nd token, and THEN the samples
        token = utils.getToken(self.get_token_url, username=self.username, password=self.password)
        retval = utils.setWorkgroup(self.endpoint_url, token, self.workgroup_name)
        token2 = utils.getToken(self.get_token_url, username=self.username, password=self.password)
        
        # We can't get all the samples from Climb at once due to the PageSize limit. Instead, we have to make successive
        # calls, incrementing the PageNumber each time, until we get fewer samples than the page size, which is set
        # in the config file.
        page_number=1
        samples = []
        logging.info(f"Getting climb samples...")
        while True:
            curr_samples = utils.getSamples(self.endpoint_url, token2, all_response=True, PageSize=self.page_size,
                PageNumber=page_number).get("data").get("items")
            samples += curr_samples
            if len(curr_samples) < self.page_size:
                # Stop when we find fewer samples than the page size.
                logging.info(f"Found {len(samples)} samples in Climb.")
                return samples
            page_number += 1
