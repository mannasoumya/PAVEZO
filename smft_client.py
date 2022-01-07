import pysftp
import sys
import os
import warnings
from uuid import uuid4
from creds import HOSTNAME, USERNAME, PASSWORD, PREFIX

download = None
check    = None
path     = ""
list_all = None

def parse_arguments(arr, argument, bool=False, verbose=False):
    for i, val in enumerate(arr):
        if val.replace("-", "") == argument:
            if bool:
                if verbose:
                    print(f"{argument} : True")
                return True
            if i+1 == len(arr):
                if verbose:
                    print(f":ERROR: No Value Passed for Argument: `{argument}`")
                raise Exception("NoValueForArgument")
            if verbose:
                print(f"{argument} : {arr[i+1]}")
            return arr[i+1]
    if verbose:
        print(f"ERROR: Argument '{argument}' not found")
    raise Exception("ArgumentNotFound")


def usage(exit_code):
    print(f"\nUsage: python {sys.argv[0]} <path> [option]")
    print("\nOPTIONS:")
    print("   -d : Download file/directory from input path")
    print("   -c : Check whether input file/directory exists")
    print("   -l : List all contents in a directory")
    print("   -h : Print this help and exit")
    print()
    if exit_code != None:
        sys.exit(exit_code)


def validate_args():
    global path
    global download
    global check
    global list_all
    if len(sys.argv) == 1:
        usage(0)

    try:
        if parse_arguments(sys.argv, 'h', True):
            usage(0)
    except Exception as e:
        pass

    path = sys.argv[1]
    
    if len(sys.argv) < 3:
        print("\nERROR: No option is provided")
        usage(1)
    
    args_cnt = 0
    try:
        download = parse_arguments(sys.argv[2:], 'd', True)
        args_cnt = args_cnt + 1
    except Exception as e:
        pass
    try:
        check = parse_arguments(sys.argv[2:], 'c', True)
        if check:
            args_cnt = args_cnt + 1
        if args_cnt > 0:
            print("\nERROR: Only one option is allowed after path")
            usage(1)
    except Exception as e:
        pass

    try:
        list_all = parse_arguments(sys.argv[2:], 'l', True)
        if list_all:
            args_cnt = args_cnt + 1
        if args_cnt > 0:
            print("\nERROR: Only one option is allowed after path")
            usage(1)
    except Exception as e:
        pass
    


def clean_path(path_prefix=""):
    global path
    if path.find(HOSTNAME) == -1:
        print(f"ERROR: '{path}' is not a valid path")
        sys.exit(1)
    new_path = path.replace(f"https://{HOSTNAME}{path_prefix}","")
    return new_path

validate_args()
warnings.filterwarnings("ignore", category=UserWarning)

new_path        = clean_path(PREFIX)
cnopts          = pysftp.CnOpts()
cnopts.hostkeys = None

try:
    sftp = pysftp.Connection(HOSTNAME, username=USERNAME,
                            password=PASSWORD, cnopts=cnopts)
except Exception as e:
    print(e)
    print("\nERROR: Cannot connect to sftp. ",end="")
    if str(e.args).find("Authentication failed") > 0:
        print("Please check creds.py file")
    print()
    sys.exit(1)
print()

if not sftp.exists(new_path):
    print(f"ERROR: '{path}' does not exists")
    print()
    sftp.close()
    sys.exit(1)

if check:
    print(f"Path: '{path}' exists\n")
    sftp.close()
    sys.exit(0)

if sftp.isfile(new_path):
    if list_all:
        print("\nERROR: Listing of files is valid only for Directories")
        print(f"'{new_path}' is a file\n")
        sftp.close()
        sys.exit(1)
    if not os.path.exists("smft_downloaded_files"):
        os.mkdir("smft_downloaded_files")
    os.chdir("smft_downloaded_files")
    print(f"\nDownloading '{path}' ==> '{(new_path.split('/'))[-1]}' ==> ",end="")
    try:
        sftp.get(new_path, preserve_mtime=True)
    except Exception as e:
        print(e)
        print(f"OOPS...Cannot Download '{path}'")
        sftp.close()
        sys.exit(1)
    
    print("Downloaded")
    print("Downloaded in folder './smft_downloaded_files/'")
else:
    if list_all:
        try:
            print(f"\n Directory Listing for '{path}':\n")
            listed_dir = sftp.listdir(new_path)
            for f_name in listed_dir:
                print(" "+f_name)
            print()
            sftp.close()
            sys.exit(0)
        except Exception as e:
            print(e)
            print(f"OOPS...Cannot List files in '{path}'")
            sftp.close()
            sys.exit(1)
    
    print(f"Path: '{path}' is a directory")
    consent = input("\nDo you want to recursively download this directory <y/n> ?\t")
    if consent.lower() == "y" or consent.lower() == "yes":
        tmp_name = str(uuid4())[:10]
        if not os.path.exists("smft_downloaded_files"):
            os.mkdir("smft_downloaded_files")
        os.chdir("smft_downloaded_files")
        os.mkdir(tmp_name)
        print(f"Downloading in 'smft_downloaded_files/{tmp_name}/'")
        try:
            sftp.get_r(new_path, tmp_name, preserve_mtime=True)
        except Exception as e:
            print(e)
            print(f"OOPS...Cannot Download '{path}'")
            sftp.close()
            sys.exit(1)
    else:
        print("\nExiting...")
        sftp.close()
        sys.exit(1)


print()
sftp.close()