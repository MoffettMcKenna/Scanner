import pprint
from pyroute2 import IPRoute
from pyroute2.iwutil import IW
from enum import Flag, auto
from AccessPoints import NetworkFactory, Radio

#######################
#                     #
#       Methods       #
#                     #
#######################

def run_scan():
    return iw.scan(wlanX)

def print_Networks(aps):
    for i in range(len(aps)):
        mac = ''
        ssid = ''
        for attr in aps[i]['attrs']:
            if attr[0] == 'NL80211_ATTR_BSS':
                for field in attr[1]['attrs']:
                    if field[0] == 'NL80211_BSS_BSSID':
                        mac = field[1]
                    elif field[0] == 'NL80211_BSS_INFORMATION_ELEMENTS':
                        ssid = field[1]['SSID'] 
                # end for field
            # end NL_80211_ATTR_BSS
        # end for attr
        print(f'{i}) {ssid}: {mac}')

def getSSID(ap):
    return ap['attrs'][3][1]['attrs'][2][1]['SSID'].decode()


########################
#                      #
#       Env Init       #
#                      #
########################

iw = IW()
ip = IPRoute()

indices = ip.link_lookup(ifname="wlan0")

if len(indices) == 1:
    wlanX = indices[0]
else:
    raise IndexError(f'WLAN0: expected len 1, found {len(indices)}')


indices = ip.link_lookup(ifname="eth0")

if len(indices) == 1:
    ethX = indices[0]
else:
    raise IndexError(f'ETH0: expected len 1, found {len(indices)}')

aps = run_scan()

points = [Radio(ap) for ap in aps]

nets = NetworkFactory.GetNetworks(points)

[print(n) for n in nets.values()]
