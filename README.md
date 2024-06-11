# MetaMap

[MetaMap](https://lhncbc.nlm.nih.gov/ii/tools/MetaMap.html) is a tool for recognizing UMLS concepts in text.
In other words, MetaMap is a NLP tool for extracting the medical words by using UMLS metathesaurus.


There are several ways to use this tool: [Interactive MetaMap](https://ii.nlm.nih.gov/Interactive/UTS_Required/MetaMap.html), [Web API](https://github.com/lhncbc/skr_web_python_api), and [Locally MetaMap](https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/run-locally/MetaMap.html).

---
### Interactive MetaMap
The interactive MetaMap is a interactive tool for MetaMap.
As shown on the [website](https://ii.nlm.nih.gov/Interactive/UTS_Required/MetaMap.html), you can type a short paragraph to **check the output that MetaMap generates**.

---
### Web API
The Web API is a Python-based API.
> [!NOTE]  
> This way seems to be the same as the original intention of Interactive metamap, **just to let you check what this tool can output**.

The author has given a great way to use it on [github](https://github.com/lhncbc/skr_web_python_api).

> [!TIP]
> This API could use on Server (Linux) not on MacOS, because something is not working for `requests-html` on MacOS.

**Before using this API**, please Sgin up [UMLS Metathesaurus Browser](https://uts.nlm.nih.gov/uts/umls/home) to get the API key. After signing in, the API is in the `My Profile`.

> [!TIP]
> The API is good, but the terminal where the database is located is very bad. 
> It runs very slowly, and after a certain amount of input, it will no longer output results, whether you change your account (email and API key) or not.
> 
> The usage code (what I write) is in `web_API folder`. I am strongly recommand to use the locally MetaMap.

---
### Locally MetaMap

Locally MetaMap is `more like a server`. 
After installation, subsequent code can be written with python code.
There are some repo show how to write python code: [pymetamap](https://github.com/AnthonyMRios/pymetamap), [Pymm](https://github.com/smujjiga/pymm).

> [!TIP]
> Before install the Locally MetaMap, please download [JAVA](www.java.com), otherwise, you will fail to run the server.

Check before install:
1. MetaMap requires a minimum of 16GB of disk space when it has been uncompressed.
2. MetaMap requires a minimum of 2GB of memory to run. At least 4GB is recommended.

We could download the Locally MetaMap [here](https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/run-locally/MainDownload.html).
And official also gives [install guide](https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/documentation/Installation.html).

> [!NOTE]  
> They give three shells the installation method, and you only need to choose the corresponding method on your own computer.

Open and stop the server (the path need be in the `public_mm`):
```
./bin/skrmedpostctl start
./bin/wsdserverctl start

./bin/skrmedpostctl stop
./bin/wsdserverctl stop
```

#### Some tips
When running the code, the API will give the error: 
`### MetaMap ERROR: Calling socket_client_open for TAGGER Server on host localhost and port 1795:
error(system_error,system_error(SPIO_E_NET_CONNREFUSED))`
The output will be gone.

In this case, please use the the `find_error.ipynb` to rerun the part which get this error.
Because I use slurm to run the code, I use the log to find the error.
You can also use the output file to find these error.

## Usage
### Sem-Types
The [documentation](https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/documentation/SemanticTypesAndGroups.html) of Semantic Types and Groups has been offered. I also download the file into `support_data` foler.
