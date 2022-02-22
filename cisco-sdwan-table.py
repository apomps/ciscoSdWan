import requests
import json
from tabulate import tabulate
import urllib3
urllib3.disable_warnings()

vmanage = "10.10.20.90"
base_url = f"https://{vmanage}:8443/"
auth_endpoint = "/j_security_check"
device_interface = "dataservice/device/interface"
omp_api = "dataservice/device/omp/summary"
bfd_api = "dataservice/device/bfd/sessions"
login_body = {"j_username": "admin","j_password": "C1sco12345"}

sess = requests.session()
login_response = sess.post(url=base_url+auth_endpoint,data=login_body, verify=False)

if not login_response.ok or login_response.text:
    print('login failed')
    import sys
    sys.exit(1)
else:
    print('login succeeded!')

site_option = input("""TYPE IN THE SITE-ID, EXAMPLE 1001, 101, blank for ALL

SITE-ID:""")

if not site_option:
    endpoint = "dataservice/device"
else:
    endpoint = "dataservice/device?site-id="+str(site_option)

devices = sess.get(url=base_url+endpoint, verify=False).json()

all_devices = []
if len(devices["data"]) == 0:
    print(f"No devices found at side id:{site_option}")
    import sys
    sys.exit(1)
else:
    for device in devices["data"]:
        interfaces = sess.get(url=base_url+device_interface+"?af-type=ipv4&deviceId="+device["deviceId"], verify=False).json()
        omp = sess.get(url=base_url+omp_api+"?deviceId="+device["deviceId"], verify=False).json()   
        bfd = sess.get(url=base_url+bfd_api+"?deviceId="+device["deviceId"], verify=False).json()
        int_list = []
        omp_list = []
        bfd_list = []
        for interface in range(len(interfaces["data"])):
            i = interfaces["data"][interface]
            int_list.append({"ifname":i["ifname"],
                    "vpn-id":i["vpn-id"],
                    "ip-address":i["ip-address"],
                    "tx-packets":i["tx-packets"] if "tx-packets" in i.keys() else "-",
                    "rx-packets":i["rx-packets"] if "rx-packets" in i.keys() else "-",
                    "if-status":i["if-admin-status"]+"/"+i["if-oper-status"],})
        for peer in range(len(omp["data"])):
            p = omp["data"][peer]
            omp_list.append({"status":p["ompuptime"]+" "+p["adminstate"]+"/"+p["operstate"],})
        for link in range(len(bfd["data"])):
            b = bfd["data"][link]
            bfd_list.append({"site-id":b["site-id"],
            "status":b["state"]+" "+b["uptime"],
            "color":b["local-color"]+"<>"+b["color"],})
        all_devices.append({"site-id":device["site-id"],
        #"deviceId":device["deviceId"],
        "host-name":device["host-name"],
        #"reachability":device["reachability"],
        #"device-model":device["device-model"],
        #"uptime-date":device["uptime-date"],
        "interfaces":tabulate(int_list,headers="keys",tablefmt="presto"),
        "omp":tabulate(omp_list,headers="keys",tablefmt="presto"),
        "bfd":tabulate(bfd_list,headers="keys",tablefmt="presto"),})

print(tabulate(all_devices,headers="keys",tablefmt="fancy_grid"))