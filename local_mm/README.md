# Local MetaMap

The `main_code.py` is used to extract words. NEED CHANGE the path from `line27-29`.

The `slurm_v1.sh` is the slurm file for running the `main_code.py`. I set up 100 machines to run at the same time (line 10). And NEED CHANGE `line 4, 17, 18` for the path of server and code.

As Readme said, the API will give you the error
`### MetaMap ERROR: Calling socket_client_open for TAGGER Server on host localhost and port 1795:
error(system_error,system_error(SPIO_E_NET_CONNREFUSED))`. In this time you need to run the `find_error.ipynb`

Copy and paste the result into `slurm_v2.sh` in the `commands`. And NEED CHANGE `line 1, 2, 3,4, 6, 18, 19`. The line 4 mentions how many machine you want to use, so that change it to the len(commands).