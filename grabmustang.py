from __future__ import division

import io
import numpy as np
import requests
import xml.etree.ElementTree as xmlet


"""
This script reads in seismic spectral Probability Density Functions (PDFs) from the MUSTANG database and plots them.
"""

class geoStation:
    def __init__(self, network, station, locations, channels, label=None):
        self.network = network
        self.station = station
        self.locations = locations
        self.channels = channels
        self.label = label
        
#    def get_station_info(self):
#        query_params = {
#            'network': self.network,
#            'station': self.station,
#            }
#       query_url = 'http://service.iris.edu/fdsnws/station/1/query'
#        rr = requests.get(url=query_url, params=query_params)
#        root = xmlet.fromstring(rr.content)
        
    def get_xml_histograms(self, start, stop):
        xml_histograms = []
        for location, channel in zip(self.locations, self.channels):
            query_params={
                'target': '{}.{}.{}.{}.M'.format(self.network, self.station, location, channel),
                'starttime': '{}'.format(start),
                'endtime': '{}'.format(stop),
                'format': 'xml',
                }
            query_url = 'http://service.iris.edu/mustang/noise-pdf/1/query'
            rr = requests.get(url=query_url, params=query_params)
            xml_histograms.append(rr)
        self.xml_histograms = xml_histograms
        
    def get_text_percentiles(self, start, stop):
        text_percentiles = []
        freqs = []
        for location, channel in zip(self.locations, self.channels):
            query_params={
                'target': '{}.{}.{}.{}.M'.format(self.network, self.station, location, channel),
                'starttime': '{}'.format(start),
                'endtime': '{}'.format(stop),
                'format': 'noiseprofile_text',
                'noiseprofile.type': ','.join([str(q) for q in np.arange(0, 101)])
                }
            query_url = 'http://service.iris.edu/mustang/noise-pdf/1/query'
            rr = requests.get(url=query_url, params=query_params)
            text_percentile = np.genfromtxt(io.StringIO(rr.content.decode('ASCII')), delimiter=',', unpack=1)
            text_percentiles.append(10**(text_percentile[1:]/10))
            freqs.append(text_percentile[0])
        self.freqs = freqs
        self.text_percentiles = text_percentiles
        
    def parse_xml_histograms(self, normed=False):
        freqs = []
        acc = []
        acc_histograms = []
        acc_percentiles = []
        for rr in self.xml_histograms:
            root = xmlet.fromstring(rr.content)
            allfreqs = np.array([np.float64(child.attrib['freq']) for child in root[-1]])
            allhits = np.array([np.float64(child.attrib['hits']) for child in root[-1]])
            allpowers = np.array([np.float64(child.attrib['power']) for child in root[-1]])
            uniquefreqs = np.unique(allfreqs)
            uniquepowers = np.unique(allpowers)
            freqs.append(uniquefreqs)
            acc.append(10**(uniquepowers / 10))
            freqs_mesh, powers_mesh = np.meshgrid(uniquefreqs, uniquepowers)
            hits_mesh = np.zeros_like(powers_mesh)
            for freq, hit, power in zip(allfreqs, allhits, allpowers):
                indices = tuple(np.argwhere(np.all([freqs_mesh==freq, powers_mesh==power], axis=0))[0])
                hits_mesh[indices] = hit
            acc_percentile = []
            for freq in uniquefreqs:
                thepowers = allpowers[allfreqs==freq]
                thehits = allhits[allfreqs==freq]
                hist_thehits = np.cumsum(thehits[np.argsort(thepowers)]) / np.sum(thehits) * 100
                percentile_powers = []
                for q in np.arange(0, 101):
                    theargs = np.argwhere(hist_thehits<=q)
                    if len(theargs) == 0:
                        theargs = np.array([0])
                    percentile_powers.append(thepowers[theargs[-1]])
                acc_percentile.append(10**(np.array(percentile_powers, dtype="object")/10))
            acc_percentiles.append(np.array(acc_percentile, dtype="object").T)
            if normed:
                hits_mesh /= np.tile(np.max(hits_mesh, axis=0), (hits_mesh.shape[0], 1))
            acc_histograms.append(hits_mesh)
        self.freqs = freqs
        self.acc = acc
        self.acc_histograms = acc_histograms
        self.acc_percentiles = acc_percentiles