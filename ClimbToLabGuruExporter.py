#!/usr/env/bin python

# Add all samples in Climb to LabGuru if not already present.
# Email a report of all samples added.

import configparser
import datetime
import logging
import os, sys

import ClimbSamples
import Emailer
import LabGuruBioCollections

class ClimbToLabGuruExporter:

    def __init__(self):
    
        """ Add all samples in Climbto LabGuru if not already present. """
        
        # Load config file, which is in the same directory as the source code.
        config = configparser.ConfigParser()
        src_dir = os.path.dirname(os.path.abspath(__file__))
        config.read(os.path.join(src_dir, "config.cfg"))

        # As this is our "main" file, we need to set up a logger.
        self.__setup_logger(config)
        
        try:
            self.climb_samples = ClimbSamples.ClimbSamples()
            self.emailer = Emailer.Emailer()
            self.labguru_collections = LabGuruBioCollections.LabGuruBioCollections()
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error(f"{exc_type}\n{fname}\n{exc_tb.tb_lineno}")
        
        
    def add_all_samples_to_labguru(self, samples):
    
        """
        
        Attempt to add all samples to LabGuru.
        
        Parameters:
            samples (list): A list of dicts, where each dict represents one sample.
            
        Returns:
            None.
            
        """
        
        try:
            num_samples_added = 0
            for sample in samples:
                # Attempt to add each sample. If successful, also keep track in the emailer, 
                # which will send a report when we're done.
                if self.labguru_collections.add_sample(sample["type"], sample["name"]):
                    num_samples_added +=1
                    self.emailer.add_sample(sample["type"], sample["name"])
            logging.info(f"Added {num_samples_added} new samples.")
            
            # Add some fake samples to the report to test formatting
            #self.emailer.add_sample("dog", "labrador")
            #self.emailer.add_sample("dog", "beagle")
            #self.emailer.add_sample("dog", "terrier")

            #self.emailer.add_sample("bird", "hawk")
            #self.emailer.add_sample("bird", "dove")
            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error(f"{exc_type}\n{fname}\n{exc_tb.tb_lineno}")
        
            
    def get_all_samples_from_climb(self):

        """ Get a list of all samples from Climb. """
        
        try:
            samples =  self.climb_samples.get_samples()
            logging.info(f"Found {len(samples)} total samples in Climb.")
            return samples
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.error(f"{exc_type}\n{fname}\n{exc_tb.tb_lineno}")

    def send_report(self):
    
        """ Email a report of all samples added. """
        
        self.emailer.send_report()
        

    def __setup_logger(self, config):

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
    try:
        exporter = ClimbToLabGuruExporter()
        samples = exporter.get_all_samples_from_climb()
        exporter.add_all_samples_to_labguru(samples)
        exporter.send_report()
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error(f"{exc_type}\n{fname}\n{exc_tb.tb_lineno}")
    