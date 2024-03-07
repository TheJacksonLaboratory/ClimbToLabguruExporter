# ClimbToLabguruExporter
  Basic tools for working with Climb and Labguru data, and a program that exports samples from Climb into Labguru if they're not already present.

## What it Does

The program will grab all samples in Climb for a given workgroup. Each sample will be added to
the appropriate custom inventory collection in Labguru, if a sample of that type with that name
does not already exist in the collection. The user can also specify that certain types of samples
in Climb be skipped entirely (not exported).

## Run Environment
The exporter currently runs twice per day on our windows server, `bhlit01wd.jax.org`. 

Here, it is deployed at `C:\source\repos\ClimbToLabguruExporter`. 

The `exporter.bat` file in this directory is scheduled and launched via the Windows Task Scheduler.

This job calls the `__main__` section of `ClimbToLabGuruExporter.py`.

The directory also contains the `config.cfg` file, which has all other pertinent run information. See below.

## The Config File

  In the file config.cfg, the user can set all of the variabes that control the program. These include:
* URL endpoints to call for the various APIs provided by Climb and Labguru
* Climb workgroup to get samples for (e.g. 'Korstanje Lab')
* sample types in Climb to be skipped
* descriptions to be given to samples when added to Labguru
* locations of password and token files
* log file directory and logging levels

## A Critical Note on the Labguru Token
The Labguru API token (see "labguru_token_file" under "[Credentials]" in the config file) expires after one year.
It was inititally issued in Dec 2022 and has now been renewed as of Feb 5 2024. When it expires again, we must request
a renewal by mailing support@biodata.com. Include the last 6 digits of the token in the body of the email when sending the renewal request.

