"""To upload files to OSF.
OSF project site - https://osf.io/bce8y/

Configuration file named .osfcli.config
should be in present working directory.
Looks like the following (without the dashed lines).

-------------------------------------------------
[osf]
username = emailofyourosfaccount@email.com
project = 5-character_osf_project_id
password = osf_password
-------------------------------------------------


Some useful details about Upload:

    -f, --force      Force overwriting of remote file
    -U, --update     Overwrite only if local and remote files differ
    -r, --recursive  Recursively upload entire directories
    
    To place contents of local directory `foo` in remote directory `bar/foo`:
    $ osf upload -r foo bar
    To place contents of local directory `foo` in remote directory `bar`:
    $ osf upload -r foo/ bar

    It will create the directory for you if uploading a file.
    Eg, uploading to code/README.md without an existing code directory is fine.
    And you can put it in / if you just want something in the home directory.

I'd like to use the -U flag but I get a path-related bug,
so I'm forcing an overwrite of everything at each upload.
"""
import os
import glob
import tqdm
import argparse
import subprocess

import utils # for directory locations


parser = argparse.ArgumentParser()
parser.add_argument("--dry", action="store_true", help="Print commands, don't run.")
args = parser.parse_args()

DRY_RUN = args.dry



# OSF docs say you can put the password in your config file, but it doesn't get picked up for me.
# So add it as an environment variable from here (I still keep it in the config file).
with open("./.osfcli.config", "r", encoding="utf-8") as f:
    for l in f.readlines():
        if l.startswith("password = "):
            password = l.split(" = ")[-1]
os.environ["OSF_PASSWORD"] = password


# def upload_cmd(f1, f2):
#     """Generate an OSF upload command."""
#     return ["osf", "upload", "-U", f1, f2]


############################## Uploading code.

# Upload all code, EXCEPT for what's in the .gitignore file.
# So have to do this a file at a time.

# Get a list of all files that are NOT ignored.
list_of_files = subprocess.check_output("git ls-files", shell=True).splitlines()
list_of_files = [ f.decode() for f in list_of_files ]

# Upload the code files to a new directory, "code" (it doesn't have to exist yet).
for fname in tqdm.tqdm(list_of_files, desc="Uploading code files"):
    command = ["osf", "upload", "--force", fname, f"code/{fname}"]
    if DRY_RUN:
        print(command) 
    else:
        subprocess.run(command)


############################## Uploading data.
####
#### Data has subdirectories, so treating them individually here.
#### Otherwise of course could just dump it all at once.


############################## Uploading source data.

# None if this right now. It's publicly available for people to access as we did.


############################## Uploading derivatives.

# Most of this "middle" output is good. Marking a few files that aren't.

EXCLUDE_FILES = [
    "r-LucidDreaming_2019April+200.csv",
    "r-LucidDreaming_2019April+200.jsonl",
    "r-LucidDreaming_2019July+200.csv",
    "r-LucidDreaming_2019July+200.jsonl",
    "doccano-disagreements_2019April.csv",
    "doccano-disagreements_2019July.csv",
    "themes-highlights.csv",
    "themes-valence.jsonl",
]

# Get a list of all files and remove those that shouldn't be uploaded.
glob_str = os.path.join(utils.Config.data_directory, "derivatives", "*")
filenames = glob.glob(glob_str)
filenames = [ fn for fn in filenames if os.path.basename(fn) not in EXCLUDE_FILES ]

# Upload derivatives, one file at a time.
for fname in tqdm.tqdm(filenames, desc="Uploading derivatives"):
    basename = os.path.basename(fname)
    command = ["osf", "upload", "--force", fname, f"data/derivatives/{basename}"]
    if DRY_RUN:
        print(command)
    else:
        subprocess.run(command)



# Don't do any of the source directory yet.

# All of the results directory can go up. It's only final values and figures.
print("Uploading all of results...")
results_directory = os.path.join(utils.Config.data_directory, "results")
command = ["osf", "upload", "--force", "-r", results_directory, "/data"]
if DRY_RUN:
    print(command)
else:
    subprocess.run(command)

