#!/usr/env/bin python

import configparser
import datetime
import logging
import os

import ClimbSamples
import LabGuruBioCollections

class ClimbToLabGuruExporter:

    def __init__(self):
    
        # Load config file, which is in the same directory as the source code.
        config = configparser.ConfigParser()
        src_dir = os.path.dirname(os.path.abspath(__file__))
        config.read(os.path.join(src_dir, "config.cfg"))

        # As this is our "main" file, we need to set up a logger.
        self.setup_logger(config)
        
        self.climb_samples = ClimbSamples.ClimbSamples()
        self.labguru_collections = LabGuruBioCollections.LabGuruBioCollections()
        
    def add_all_samples_to_labguru(self, samples):
    
        """
        
        Attempt to add all samples to LabGuru.
        
        Parameters:
            samples (list): A list of dicts, where each dict represents one sample.
            
        Returns:
            None.
            
        """
        
        for sample in samples:
            self.labguru_collections.add_sample(sample["type"], sample["name"])
            
            
    def get_all_samples_from_climb(self):

        """ Get a list of all samples from Climb. """
        
        samples =  self.climb_samples.get_samples()
        logging.info(f"Found {len(samples)} total samples in Climb.")
        return samples


    def setup_logger(self, config):

        """ Setup logger. """

        # Get the log file's directory.
        log_dir = config["logging"]["log_dir"]

        # If the directory doesn't exist, make it
        if not os.path.isdir(log_dir):
            try:
                pathlib.Path(log_dir).mkdir(parents = True, exist_ok = True)
            except Exception as e:
                sys.exit(f"Attempt to make logging directory {log_dir} failed, received exception {str(e)}") 

        # Create the log file, with a timestamp in its name, and get its full path
        log_file = "climb_to_labguru_export_log_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".txt"
        log_path = os.path.join(log_dir, log_file)
        print(f"Log file located at {log_path}")

        # Get the desired log level
        log_level = logging.getLevelName(config["logging"]["level"])

        # Now configure the logger with the established parameters.
        logging.basicConfig(filename=log_path, filemode='w', level=log_level,
            format='%(asctime)s %(levelname)s: %(message)s')


if __name__ == "__main__":
    exporter = ClimbToLabGuruExporter()
    samples = exporter.get_all_samples_from_climb()
    exporter.add_all_samples_to_labguru(samples)
    