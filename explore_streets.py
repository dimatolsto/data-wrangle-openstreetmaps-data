# -*- coding: utf-8 -*-
"""
Created on Tue May 12 16:34:16 2015

@author: DT
"""

"""
Your task in this exercise has two steps:

- audit the OSMFILE and change the variable 'mapping' to reflect the changes needed to fix 
    the unexpected street types to the appropriate ones in the expected list.
    You have to add mappings only for the actual problems you find in this OSMFILE,
    not a generalized solution, since that may and will depend on the particular area you are auditing.
- write the update_name function, to actually fix the street name.
    The function takes a string with street name as an argument and should return the fixed name
    We have provided a simple test so that you see what exactly is expected
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "sample_1_pct.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

street_mapping = { "St": "Street", "St.": "Street", "street": "Street", "Ave": "Avenue", \
    "ave": "Avenue", "avenue": "Avenue",  "Rd.": "Road", \
    "N.": "North", "S.": "South", "W.": "West", "E.": "East"}       


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in street_mapping:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types


def update_street_name(name):
    '''    
    Fix the unexpected street types as keys in the given street_mapping dict 
    to the appropriate ones as valuess in the street_mapping.
    '''
#    street_mapping = { "St": "Street", "St.": "Street", "street": "Street", "Ave": "Avenue", \
#    "ave": "Avenue", "avenue": "Avenue",  "Rd.": "Road", \
#    "N.": "North", "S.": "South", "W.": "West", "E.": "East"}
    
    name_list = name.split()
    new_name = ""
    
    for name_check in name_list:
        if name_check in street_mapping:
            name_check = street_mapping[name_check]#.strip()
        new_name = new_name + " " + name_check
    try:
        name = new_name.lstrip()#.encode('ascii', 'ignore')
        return name
    except:
        return None

    

    return name


if __name__ == '__main__':
    st_types = audit(OSMFILE)
    pprint.pprint(dict(st_types))