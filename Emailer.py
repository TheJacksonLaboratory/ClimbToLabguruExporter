#!/usr/bin/env pytyhon

# Format and email a report on what samples were added

from collections import defaultdict
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
import smtplib


class Emailer:

    """
    Format reports and send email notifications to recipients.
    """

    def __init__(self):

        """
        Read and parse config file
        """

        # Load config file, which is in the same directory as the source code.
        config = configparser.ConfigParser()
        src_dir = os.path.dirname(os.path.abspath(__file__))
        config.read(os.path.join(src_dir, "config.cfg"))

        self.mail_conf = config["emailer"]

        # The domain and port number are fixed constants
        self.smtp_obj = smtplib.SMTP(self.mail_conf["smtp_address"], self.mail_conf["smtp_port"])

        # Keep a collection of all samples added as a dict of lists, where each key is a sample
        # type and the value is a list of all samples of that type. 
        self.all_samples = defaultdict(list)
        
        # Save the name of the workgroup, to be included in the report
        self.climb_workgroups = [x.strip() for x in config["climb"]["workgroup_names"].split(',')]
        
    def add_sample(self, sample_type, sample_name):
    
        """
        Add a new sample to the report. 
        """
        
        # Just the sample to the corresponding list for it's type.
        self.all_samples[sample_type].append(sample_name)
        
    def format_report(self):

        """
        Prepare a report to be emailed.
        """

        msg = MIMEMultipart()
        msg["From"] = self.mail_conf["From"]
        msg["To"] = self.mail_conf["To"]
        msg["Subject"] = ','.join(self.climb_workgroups) + ' ' + self.mail_conf["Subject"]
        msg.attach(MIMEText(self.get_report_body(), 'html'))
        return msg


    # Do the HTML formatting of the report body
    def get_report_body(self):

        """
        Do the layout and HTML formatting of the report body
        """

        # Start with the html header
        html_text = "<html>\n    <head></head>\n    <body>\n"
        
        # Begin with the total number of samples, written in bold
        total_num_samples = sum(len(samples) for samples in self.all_samples.values())
        html_text += f'      <b><h1 style="font-size: 18;">{total_num_samples} New Samples Added </h1></b>'
        
        # For each sample type, write the type and number in bold
        for sample_type, curr_samples in self.all_samples.items():
            html_text += f'      <b>{sample_type}: {len(curr_samples)} Samples Added</b><br>\n'
            
            #follow with a list of samples as a string
            samples_str = ', '.join(curr_samples)
            html_text += f'      {samples_str}<br><br>\n'

        # End with the html close tags
        html_text += "    <body>\n</html>\n"
        return html_text


    def send_report(self):

        """
        Email a formatted report
        """

        msg = self.format_report()

        logging.info(f'Sending report to: {msg["To"]}')
        logging.debug(f"Report is: \n{msg.as_string()}")

        # Open a connection to the SMPTP server.
        self.smtp_obj = smtplib.SMTP(self.mail_conf["smtp_address"], self.mail_conf["smtp_port"])

        # sendmail should return nothing if everything worked ok. The comma-delimited
        # list of recipients needs to be split, with empty entries removed
        val = self.smtp_obj.sendmail(msg["From"],
                                     [x for x in msg["To"].split(',') if x],
                                     msg.as_string())
        if val:
            logging.error(f"sendmail returned: {val}")
        



