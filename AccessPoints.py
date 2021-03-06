import pprint
from pyroute2 import IPRoute
from pyroute2.iwutil import IW
from enum import Flag, auto

# todo add annotations

class WifiRevs(Flag):
    a = auto()
    b = auto()
    g = auto()
    n = auto()
    ac = auto()


class Radio:
    """
    The Access Point is the single channel station - an actual wifi router will 
    put out multiple frequency/SSID/channel sets.  The full set will be 
    encapsulted in the Router class.  So really this is jut a single radio.
    """

    def __init__(self, radioTxt):
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
        for a in radioTxt['attrs']:

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


class NetworkFactory:
    
    @classmethod
    def GetNetworks(cls, radios):
        nets = {} # declare our return value as an empty dict
        
        # process all the access points
        for r in radios:

            # if the network hasn't been seen yet create a new one
            if r.ssid not in nets.keys():
                nets[r.ssid] = Network(r)
            # if the network exists add a new acces point
            else:
                nets[r.ssid].Add(r)

            # add the AccessPoint to the network
            nets[r.ssid].Add(r)

        # end for ap

        return nets
    #end GetNetworks()


class Network:
    """
    This represents a single router, access point, station, or network.  Any 
    radio with a shared SSID is part of a single network.
    """
    
    def __init__(self, rd):
        """
        Create a new Router with 
        """
        self.Name = rd.ssid if len(rd.ssid) > 0 else '<Unknown>'
        self._macs = {rd.mac: rd}

    def Add(self, rd):
        self._macs[rd.mac] = rd

    def __str__(self):
        ret = self.Name + "\n"
        for n in self._macs.values():
            ret = ret + f'\t{n.mac}\n'
        return ret




