# -*- coding: utf-8 -*-
"""
Created on Sat May 09 17:36:59 2015

@author: DT
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
"""
Here we modified the script tags.py from the lesson 6. 
We check the "k" value for each "<tag>" and see if they can be valid keys in MongoDB,
as well as see if there are any other potential problems.

We use regular expressions to check for certain patterns
in the tags. 
We would like to change the data model
and expand the "addr:street" type of keys to a dictionary like this:
{"address": {"street": "Some value"}}
So, we have to see if we have such tags, and if we have any tags with problematic characters.

The script returns the number of patterns, the set of samples of patterns and the set of nodes.

"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
lower_colon_double = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')


def key_type(element, keys):
    

    if element.tag == "tag":
        # YOUR CODE HERE
        for tag in element.iter("tag"):
            #print tag.attrib['k']
            if lower.search(tag.attrib['k']):
                keys['lower'][0] += 1
                keys['lower'][1].add(tag.attrib['k'])
                #print tag.attrib['k']
            elif lower_colon.search(tag.attrib['k']):
                keys['lower_colon'][0] += 1
                keys['lower_colon'][1].add(tag.attrib['k'])
                #print tag.attrib['k']
            elif problemchars.search(tag.attrib['k']):
                keys['problemchars'][0] += 1
                keys['problemchars'][1].add(tag.attrib['k'])
                #print tag.attrib['k']
            elif lower_colon_double.search(tag.attrib['k']):
                keys['lower_colon_double'][0] += 1    
                keys['lower_colon_double'][1].add(tag.attrib['k'])
            else:
                keys['other'][0] += 1
                keys['other'][1].add(tag.attrib['k'])
                
            if tag.attrib['k'] == "addr:postcode":
                    if not is_postcode_correct(tag.attrib['v']):
                        keys['postcode'][0] += 1
                        keys['postcode'][1].add(tag.attrib['v'])    
                        
#                print node


    return keys

def is_postcode_correct(postcode):
    '''
    Check if the postcode is correct. It must have 5 digits 
    and belong to the NYC postcodes   
    '''
    if len(postcode) == 5:
        try:
            code = int(postcode)
            if code > 10000 and code < 11693: # NYC postcodes
                return True
            else:              
                return False
        except:        
            return False
    else:
        return False


def process_map(filename):
    keys = {"lower": [0,set()], "lower_colon": [0,set()], "problemchars": [0,set()], \
    "lower_colon_double":[0,set()], "other": [0,set()], "postcode": [0,set()]}    
    tags = set()
    
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
        tags.add(element.tag)
    return keys, tags


if __name__ == "__main__":
    keys, tags = process_map('sample_1_pct.osm')
    pprint.pprint(keys)
    pprint.pprint(tags)