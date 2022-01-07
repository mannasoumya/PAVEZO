# SFTP Client in Python

## Just a Toy Wrapper Over ['pysftp'](https://pypi.org/project/pysftp/) 
#### Nothing fancy

### Quick Start

```console
> pip install -r requirements.txt
> python smft_client.py

Usage: python smft_client.py <path> [option]

OPTIONS:
   -d : Download file/directory from input path
   -c : Check whether input file/directory exists
   -l : List all contents in a directory
   -h : Print this help and exit

> python smft_client.py https://{HOSTNAME}/{PREFIX}/{FILE_PATH} -d


Downloading 'https://{HOSTNAME}/{PREFIX}/{FILE_PATH}' ==> 'FILE_NAME' ==> Downloaded
Downloaded in folder './smft_downloaded_files/'

```
**Check [creds.py](./creds.py) file for Credentials**