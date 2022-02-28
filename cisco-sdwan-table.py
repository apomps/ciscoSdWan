import requests
import json
from tabulate import tabulate
import time
from datetime import datetime
import urllib3
urllib3.disable_warnings()
import itertools
import sys
import threading

vmanage = "10.10.20.90"
base_url = f"https://{vmanage}:8443/"
auth_endpoint = "/j_security_check"
device_interface = "dataservice/device/interface"
omp_api = "dataservice/device/omp/summary"
bfd_api = "dataservice/device/bfd/sessions"
tunnel_api = "dataservice/device/tunnel/statistics"
login_body = {"j_username": "admin","j_password": "C1sco12345"}

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

def sdwan_table(site_option):
    sess = requests.session()
    try:
        login_response = sess.post(url=base_url+auth_endpoint,data=login_body, verify=False)
    except Exception as e:
        print("login failed")
        print(e)
        print("\n")
        sess.close()
        return None
    else:
        if not login_response.ok or login_response.text:
            print("Login failed. Confirm credentials")
            sess.close()
            return None
        else:
            print("\rLogin succeeded!")
        
        if not site_option:
            endpoint = "dataservice/device"
        else:
            endpoint = "dataservice/device?site-id="+str(site_option)
        
        devices = sess.get(url=base_url+endpoint, verify=False).json()
        
        all_devices = []
        if len(devices["data"]) == 0:
            print(f"No devices found at side id:{site_option}")
            return None
        else:
            for device in devices["data"]:
                print("\r"+"Site:"+str(device["site-id"])+" "+"["+str(len(devices["data"]))+"/"+str(devices["data"].index(device)+1)+"] - "+
                str(device["deviceId"])+" "+str(device["host-name"])+" "+str(device["device-model"]))
                if device["reachability"] == "reachable":
                    interfaces = sess.get(url=base_url+device_interface+"?af-type=ipv4&deviceId="+device["deviceId"], verify=False).json()
                    omp = sess.get(url=base_url+omp_api+"?deviceId="+device["deviceId"], verify=False).json()   
                    bfd = sess.get(url=base_url+bfd_api+"?deviceId="+device["deviceId"], verify=False).json()  
                    tunnel = sess.get(url=base_url+tunnel_api+"?deviceId="+device["deviceId"], verify=False).json()
                    int_list = []
                    omp_list = []
                    bfd_list = []
                    for interface in range(len(interfaces["data"])):
                        i = interfaces["data"][interface]
                        int_list.append({"ifname":i["ifname"],
                                "vpn-id":i["vpn-id"],
                                "ip-address":i["ip-address"],
                                "tx-pkts/rx-pkts":str(i["tx-packets"] if "tx-packets" in i.keys() else "-")+" / "+str(i["rx-packets"] if "rx-packets" in i.keys() else "-"),
                                "if-status":i["if-admin-status"]+"/"+i["if-oper-status"],})
                    for peer in range(len(omp["data"])):
                        p = omp["data"][peer]
                        omp_list.append({"status":p["adminstate"]+"/"+p["operstate"]+" "+p["ompuptime"],})
                    for link in range(len(bfd["data"])):
                        b = bfd["data"][link]
                        for t in tunnel["data"]:
                            if t["dest-ip"] == b["dst-ip"]:
                                bfd_list.append({"site-id":b["site-id"],
                                    "status":b["state"]+" "+b["uptime"],
                                    "tx_pkts/rx_pkts": str(t["tx_pkts"])+" / "+str(t["rx_pkts"]),
                                    "color":b["local-color"]+"<>"+b["color"],
                                    "src-ip":b["src-ip"],
                                    "dest-ip": t["dest-ip"],})
                        for int in int_list:
                            for b in bfd_list:
                                if int["ip-address"].split("/")[0] == b["src-ip"]:
                                    b["src-ip"] = int["ifname"]

                    all_devices.append({"site-id":device["site-id"],
                    "host-name":device["host-name"],
                    "uptime-date":str(datetime.now() - datetime.fromtimestamp(device["uptime-date"]//1000)),
                    "interfaces":tabulate(int_list,headers="keys",tablefmt="simple",disable_numparse=True),
                    "omp":tabulate(omp_list,headers="keys",tablefmt="simple"),
                    "bfd":tabulate(bfd_list,headers="keys",tablefmt="simple",disable_numparse=True),})
                else:
                    all_devices.append({"site-id":device["site-id"],
                    "host-name":device["host-name"],
                    "reachability":device["reachability"],
                    })
        print("\n")
        print(tabulate(all_devices,headers="keys",tablefmt="fancy_grid"))

if __name__ == "__main__":
    site_option = input("""
    TYPE IN THE SITE-ID, EXAMPLE 1001, 101, blank for ALL
    SITE-ID:""")
    loading_process = threading.Thread(target=spin_load)
    loading_process.start()
    sdwan_table(site_option)
    script_done = True
