# ClimbToLabguruExporter
  Basic tools for working with Climb and Labguru data, and a program that exports samples from Climb into Labguru if they're not already present.

## To Run

$ python ClimbToLabguruExporter.py

## What it Does

The program will grab all samples in Climb for a given workgroup. Each sample will be added to
the appropriate custom inventory collection in Labguru, if a sample of that type with that name
does not already exist in the collection. The user can also specify that certain types of samples
in Climb be skipped entirely (not exported).

## The Config File

  In the file config.cfg, the user can set all of the variabes that control the program. These include:
* URL endpoints to call for the various APIs provided by Climb and Labguru
* Climb workgroup to get samples for (e.g. 'Korstanje Lab')
* sample types in Climb to be skipped
* descriptions to be given to samples when added to Labguru
* locations of password and token files
* log file directory and logging levels



