[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/apomps/ciscoSdWan)
# Python script for Cisco SD-WAN
This python script gathers operational information from Cisco SD-WAN fabric components, leveraging vManage APIs and generates a tabular view.

This script was built to interact with the [Cisco DevNet Reservable Sandbox for SD-WAN 20.4](https://devnetsandbox.cisco.com/RM/Diagram/Index/4a0f4308-1fc4-4f4c-ae8c-2734f705bd21?diagramType=Topology). So the credentials used to authenticate towards the vManage are only applicable to the Cisco Sandbox. If used in another enviornment the varibles below would need to be changed.

| Variable | Type | Content |
| --- | --- | --- |
| `vmanage = "10.10.20.90"` | string | IP address of the vManage |
| `login_body = {"j_username": "admin", "j_password": "C1sco12345"}` | dictionary | Credentials for POST request Payload |

## API used for this project
| Method | API path |
| --- | --- |
| `POST` | `/j_security_check` |
| `GET` | `/dataservice/device/interface` |
| `GET` | `/dataservice/device/omp/summary` |
| `GET` | `/dataservice/device/bfd/sessions` |
| `GET` | `/dataservice/device/tunnel/statistics` |

For more information on available [vManage APIs v20-4](https://developer.cisco.com/docs/sdwan/#!sd-wan-vmanage-v20-4):

### Requirements
```
Python >= 3.9
tabulate==0.8.9
requests==2.27.1
```
more information on [tabulate](https://pypi.org/project/tabulate/) and
[requests](https://pypi.org/project/requests/)
### Install requirements
```
git clone https://github.com/apomps/ciscoSdWan
cd ciscoSdWan
pip install -r requirements.txt
```

## Cool loading bar
Instead of looking at a blank screen wondering if the script is running or not. There is a simple function using built-in modules that will iterate through a list, printing strings giving a cool loading/processing view. There are 3 options that I've found very cool and liked all 3! So just uncomment the most prefered.
```
import itertools
import sys
import threading
import time

#spin = ["⢿ ", "⣻ ", "⣽ ", "⣾ ", "⣷ ", "⣯ ", "⣟ ", "⡿ "]
#spin = [ "[|]", "[/]", "[-]", "[\\]"]
spin = ["[■□□□□□□□□□]","[■■□□□□□□□□]", "[■■■□□□□□□□]", "[■■■■□□□□□□]", "[■■■■■□□□□□]", "[■■■■■■□□□□]", "[■■■■■■■□□□]", "[■■■■■■■■□□]", "[■■■■■■■■■□]", "[■■■■■■■■■■]"]
script_done = False
def spin_load():
    for i in itertools.cycle(spin):
        if script_done:
            break
        else:
            sys.stdout.write("\r"+i+" ")
            time.sleep(0.1)
            sys.stdout.flush()
```
## Example Output - all
In this output, it successfully authenticated to the Cisco SDWAN Sandbox vManage, collected information from all components in the topology. Since I executed it very early in the reservation window, not all the devices were fully up/reachable and there was no bfd sessions available. In a real world scenario this would not be a "prefered" output.
![sdwan-script-output-all](https://user-images.githubusercontent.com/68168232/156904042-1d5eb941-68f5-4b81-a14f-35709eb2a3bd.PNG)

## Example Output - site id
In this output, typing the site id "1003", which is a valid within the enviornment, it executed GET requests for only devices part of that site id. As the enviornment was running for more time, there was more information from the vEdge (e.g: omp, bfd).
![sdwan-script-output-1003](https://user-images.githubusercontent.com/68168232/156904047-479c911b-0676-4f5e-a9f0-8ebde2c75b66.PNG)

## Example Output - ssh directly to vEdge
In this output, is an example if needed to collect the same information, however ssh to vEdge directly.
![sdwan-putty-output-1003](https://user-images.githubusercontent.com/68168232/156904050-cc169c9e-5a03-48e0-ada7-62a818d040fe.PNG)

# About me!
I'm Arthur Pompeu, I'm a Network Engineer and very excited about finding new and creative ways to automate just about... anything!

Hope this code helps you in some way!

You can find me on [LinkedIn](https://linkedin.com/in/arthur-pompeu-3459bb23)

