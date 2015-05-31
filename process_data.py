# -*- coding: utf-8 -*-
"""
Created on Tue May 12 16:00:08 2015

@author: DT

This code wrangles the data and transform the shape of the data
into the model suitable for MongoDB. The output is a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json

from explore_tags import is_postcode_correct
from explore_streets import update_street_name

#lower = re.compile(r'^([a-z]|_)*$')
#lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\.\\ \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]



def shape_element(element):
    '''
    The function does the following things:
    - we process only 2 types of top level tags: "node" and "way"
    - all attributes of "node" and "way" are turned into regular key/value pairs, except:
        - attributes in the CREATED array are added under a key "created"
        - attributes for latitude and longitude are added to a "pos" array,
          for use in geospacial indexing. The values inside "pos" array are floats. 
    - if second level tag "k" value contains problematic characters, it is ignored
    - if second level tag "k" value starts with "addr:", it is added to a dictionary "address"
    - if second level tag "k" value does not start with "addr:", but contains ":", we process it
      same as any other tag.
      Similarly, we deal with: 
        "gnis:" 
        "railway:"    
        "tiger:"
        "cityracks."
        "contact:"
        "source:"
        "building:"
    - if there is a second ":" that separates the type/direction of a street etc.,
      the tag is ignored, for example:
    
    <tag k="addr:housenumber" v="5158"/>
    <tag k="addr:street" v="North Lincoln Avenue"/>
    <tag k="addr:street:name" v="Lincoln"/>
    <tag k="addr:street:prefix" v="North"/>
    <tag k="addr:street:type" v="Avenue"/>
    <tag k="amenity" v="pharmacy"/>
    
      is turned into:
    
    {...
    "address": {
        "housenumber": 5158,
        "street": "North Lincoln Avenue"
    }
    "amenity": "pharmacy",
    ...
    }
    
    - for "way" specifically:
    
      <nd ref="305896090"/>
      <nd ref="1719825889"/>
    
    is turned into
    "node_refs": ["305896090", "1719825889"] 
    
    We correct street names.
     We correct postcodes.
    '''
    node = {}
    if element.tag == "node" or element.tag == "way" :
        
       
        # initialize dictionaries
        created = {}
        pos = [None,None]
        address = {}        
        gnis = {} 
        railway = {}     
        tiger = {}
        cityracks = {}
        contact = {}
        source = {}
        building = {}
        
        
       
        # Shape created dict
        for attr in element.attrib:
            if attr in CREATED:
                created[attr] = element.attrib[attr]
            elif attr == 'lat':
                pos[0] = float(element.attrib[attr])
            elif attr == 'lon':
                pos[1] = float(element.attrib[attr])                
            else:              
                node[attr] = element.attrib[attr]
        node['created'] = created
        if pos != [None,None]:
            node['pos'] = pos


        for tag in element.iter('tag'):
            # pass problematic keys
            if problemchars.search(tag.attrib['k']) and \
            not re.compile(r'^(cityracks.)').search(tag.attrib['k']):
                continue
            # pass keys with multiple ":" separators
            elif len(tag.attrib['k'].split(":")) > 2:
                continue                 
            
            # Shape addr:            
            elif re.compile(r'^(addr:)').search(tag.attrib['k']):
                # fix street name
                if tag.attrib['k'] == "addr:street": 
                    tag.attrib['v'] = update_street_name(tag.attrib['v'])
                # check postcode
                if tag.attrib['k'] == "addr:postcode":
                    if not is_postcode_correct(tag.attrib['v']):
                        tag.attrib['v'] = update_postcode(tag.attrib['v'])
                        if tag.attrib['v'] == 'wrong postcode':
                            continue
                address[tag.attrib['k'].split(":")[1]] = tag.attrib['v']
            
            # shape gnis:    
            elif re.compile(r'^(gnis:)').search(tag.attrib['k']):
                gnis[tag.attrib['k'].split(":")[1]] = tag.attrib['v']    
            
            # shape railway:    
            elif re.compile(r'^(railway:)').search(tag.attrib['k']):
                railway[tag.attrib['k'].split(":")[1]] = tag.attrib['v'] 
                    
            # shape tiger:    
            elif re.compile(r'^(tiger:)').search(tag.attrib['k']):
                # shape v arrays
                v_list = tag.attrib['v'].split(";")
                v_vals = []
                for v in v_list:
                    v_vals.append(v.strip())
                tiger[tag.attrib['k'].split(":")[1].lower()] = v_vals

            # shape cityracks:    
            elif re.compile(r'^(cityracks.)').search(tag.attrib['k']):
                cityracks[tag.attrib['k'].split(".")[1]] = tag.attrib['v']
                
            # Shape contact:            
            elif re.compile(r'^(contact:)').search(tag.attrib['k']):
                contact[tag.attrib['k'].split(":")[1]] = tag.attrib['v']    
                
            # Shape source:            
            elif re.compile(r'^(sourse:)').search(tag.attrib['k']):
                source[tag.attrib['k'].split(":")[1]] = tag.attrib['v']    
                
            # Shape building:            
            elif re.compile(r'^(building:)').search(tag.attrib['k']):
                building[tag.attrib['k'].split(":")[1]] = tag.attrib['v'] 
                
            else:
                node[tag.attrib['k']] = tag.attrib['v']
                
        if len(address) > 0:
            node['address'] = address
            
        if len(gnis) > 0:
            node['gnis'] = gnis      
            
        if len(railway) > 0:
            node['railway'] = railway 
            
        if len(tiger) > 0:
            node['tiger'] = tiger
            
        if len(cityracks) > 0:
            node['cityracks'] = cityracks  
            
        if len(source) > 0:
            node['source'] = source    
            
        if len(building) > 0:
            node['building'] = building            
        
        
        node_refs = []
        #if element.tag == "way":
        for nd in element.iter('nd'):
            node_refs.append(nd.attrib['ref'])
        if len(node_refs) > 0:
            node['node_refs'] = node_refs
            

        if element.tag == "way":        
            node['type'] = 'way'
        if element.tag == "node":
            node['type'] = 'node'
        
        return node
        
    else:
        return None
        


#def update_street_name(name):
#    '''    
#    Fix the unexpected street types as keys in the given street_mapping dict 
#    to the appropriate ones as valuess in the street_mapping.
#    '''
#    street_mapping = { "St": "Street", "St.": "Street", "street": "Street", "Ave": "Avenue", \
#    "ave": "Avenue", "avenue": "Avenue",  "Rd.": "Road", \
#    "N.": "North", "S.": "South", "W.": "West", "E.": "East"}
#    
#    name_list = name.split()
#    new_name = ""
#    for name_check in name_list:
#        if name_check in street_mapping:
#            name_check = street_mapping[name_check]#.strip()
#        new_name = new_name + " " + name_check
#    try:
#        name = new_name.lstrip()#.encode('ascii', 'ignore')
#        return name
#    except:
#        return None
    
    
    
#def is_postcode_correct(postcode):
#    '''
#    Check if the postcode is correct. It must have 5 digits 
#    and belong to the NYC postcodes   
#    '''
#    if len(postcode) == 5:
#        try:
#            code = int(postcode)
#            if code > 10000 and code < 11693: # NYC postcodes
#                return True
#            else:              
#                return False
#        except:        
#            return False
#    else:
#        return False
        

def update_postcode(postcode):
    '''
    Correct cases like 'NY 10533' or '11229-8541'
    '''  
    #cases like 'NY 10533'
    codes = postcode.split() #cases like 'NY 10533'
    for code in codes:
        if is_postcode_correct(code):
            return code
        else:
            continue
    #cases like '08901-8541', '089018541'    
    code = postcode[:5]
    if is_postcode_correct(code):
            return code
    #other cases
    return 'wrong postcode'
    


def process_map(file_in, pretty = False):
    '''
    shape elements from input osm file and convert it to json file
    '''
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
                element.clear()
    return data


if __name__ == "__main__":
    data = process_map('new-york_new-york.osm', False)
#    data = process_map('sample_1_pct.osm', True)    
#    pprint.pprint(data)