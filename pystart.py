import pprint
from pyroute2 import IPRoute
from pyroute2.iwutil import IW
from enum import Flag, auto


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
#       Classess       #
#                      #
########################

class WifiRevs(Flag):
    a = auto()
    b = auto()
    g = auto()
    n = auto()
    ac = auto()


class AccessPoint:

    def __init__(self, ap):
        self.mac = ''
        self.ssid = ''
        self.rates = []
        self.stars = []
        self.exrates = []
        self.frequency = 0
        self.channel = 0
        self.signal = 0
        self.width = 0

        # process this is in one big loop
        for a in ap['attrs']:

            # the BSS Attributes hae the meat of the access point data
            if a[0] == "NL80211_ATTR_BSS":
                #convience variable
                attrs = a[1]['attrs']
                for attr in attrs:
                    if attr[0] == 'NL80211_BSS_BSSID': # aka the mac address
                        self.mac = attr[1]
                    elif attr[0] == 'NL80211_BSS_FREQUENCY': # this will be part of determining type
                        self.frequency = attr[1]
                    elif attr[0] == 'NL80211_BSS_SIGNAL_MBM':
                        self.signal = attr[1]['VALUE']  # this is a raw value, unit conversion happens in Signal_Strength 
                    elif attr[0] == 'NL80211_BSS_CHAN_WIDTH':
                        self.width = attr[1]
                    elif attr[0] == 'NL80211_BSS_INFORMATION_ELEMENTS': # these are key
                        ies = attr[1]
                        
                        #read the ssid - aka the name of the access point
                        name = ies.get('SSID', None)
                        if name is not None:
                            self.ssid = name.decode()
                        
                        # read out the channel - a key element to dtermine protocol generation
                        chan = ies.get('CHANNEL', None)
                        if chan is not None:
                            self.channel = chan
                           
                        rates = ies.get('SUPPORTED_RATES', None)
                        if rates is not None and len(rates) > 0:
                            # not sure why some of these have stars and some don't
                            for x in rates.split(' '):
                                # skip the empties - always happens at the end of the list
                                if len(x) == 0:
                                    continue
                                # strip the stars after saving them special
                                if x.endswith('*'):
                                    x = x.rstrip('*')
                                    self.stars.append(x)
                                # now save anything with length
                                self.rates.append(x)

                        rates = ies.get('EXTENDED_RATES', None)
                        if rates is not None and len(rates) > 0:
                            # not sure why some of these have stars and some don't
                            for x in rates.split(' '):
                                # skip the empties - always happens at the end of the list
                                if len(x) == 0:
                                    continue
                                # strip the stars after saving them special
                                if x.endswith('*'):
                                    x = x.rstrip('*')
                                    self.stars.append(x)
                                # save this in the extended list
                                self.exrates.append(x)
                                # now save them all
                                self.rates.append(x)
                    # end if attr[0]'s
                #end for attr in attrs
            # end if ATTR_BSS
        # end for a in attrs

        # we could do the request of it, but it's all just parts of the 
        # nl80211 command so we won't get anything usefull
    #end init

    def __str__(self):
        return f'{self.ssid} ({self.mac})\n\tSIG:{self.signal}\tChannel:{self.channel}\tFREQ:{self.frequency}\tWIDTH:{self.width}\n{self.rates}\n{self.stars}\n{self.exrates}\n'

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

points = [AccessPoint(ap) for ap in aps]

for pt in points:
    if pt.ssid == 'CloudCity':
        print(pt)
