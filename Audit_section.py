
# coding: utf-8

# In[25]:

# Importing required packages
import xml.etree.ElementTree as ET
import pprint
import re
from collections import defaultdict


#Counting the total no. of tags in osm file 
def tags_count(OSM_file):
    tags_dict={}
    for event,element in ET.iterparse(OSM_file):
        if element.tag not in tags_dict:
            tags_dict[element.tag] = 1
        else:
            tags_dict[element.tag] += 1    
    return tags_dict
OSM_file='las-vegas_nevada_sample.osm'
tags_count(OSM_file)


# In[26]:


'''
Auditing Street Names Section
These section audits and updates the street names with updated names

'''
osm_file = open("las-vegas_nevada_sample.osm", "r")

street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)


expected=["Street","Avenue","Boulevard","Drive","Apache","Circle",
          "Lane","Parkway","Road","Street","South"]

mapping={
         "St":"Street",
         "St.":"Street",
         "AVE":"Avenue",
         "Ave":"Avenue",
         "ave":"Avenue",
         "Ave.":"Avenue",
         "blvd":"Boulevard",
         "Blvd":"Boulevard",
         "Blvd.":"Boulevard",
         "Cir":"Circle",
         "Circolo":"Circle",
         "Dr":"Drive",
         "Dr.":"Drive",
         "ln":"Lane",
         "Ln":"Lane",
         "Ln.":"Lane",
         "parkway":"Parkway",
         "Pkwy":"Parkway",
         "Rd":"Road",
         "Rd.":"Road",
         "Rd5":"Road",
         "S":"South",
         "S.":"South"
        }

## Section of auditing street map
## Used the Case Study
'''
audit_street_type function:This function searches for desired regular expression
and adds them onto a set if it is not in expected format.
is_street_name function:This function checks for attribute "addr:street"
audit function:Responsible for returning street_types set
update_name function:Updates name by substituting the variable to mapping dictionary
updated_street_name function:This is required in the data.py
test function:tests whether they are changed properly or not
'''
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
    
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osm_file):
    street_types=defaultdict(set)
    for event, elem in ET.iterparse(osm_file,events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])    
    osm_file.close()
    return street_types
    
def update_name(name,mapping):
    m=street_type_re.search(name)
    street_type=m.group()
    if m:
        street_type = m.group()
        if street_type not in expected:
            if street_type in mapping.keys():
                name = re.sub(street_type_re, mapping[street_type], name)
    return name 

def updated_street_name(elem):
    updated_name=update_name(elem.attrib['v'],mapping)
    return updated_name

def test():
    street_types_set=audit(osm_file)
    # pprint.pprint(dict(street_types_set))

    for street_type,ways in street_types_set.iteritems():
        for name in ways:
            better_name=update_name(name,mapping)
            print name,"=>",better_name
            
if __name__=='__main__':
    test()


# In[27]:


'''
Auditing postcodes
post_code_re=re.compile(r'(^(89)\d{3}$)|(^(89)\d{3}-\d{4}$)')
Explanation:Las Vegas begins postcode with 89 hence I used a OR(|)in this scenario
E.g. 89052 ,89147-8491
post_code_re_NV=re.compile(r'^(NV)\s(89)\d{3}$')
Explanation:NV is short for Nevada e.g.NV 89119
post_code_re_Nevada=re.compile(r'(Nevada)\s(89)\d{3}')
Explanation:e.g.Nevada 89113

audit_postcode function:Searches for regular expressions and adds them onto the set
is_postcode function:Function checks attribute for "addr:postcode"
postcode_audit function:After successfully putting them in set these are returned
update_postcode function:updates the postcode 
updated_postcode function:function required in data.py
test function:Test if it is properly audited

'''
osm_file = open("las-vegas_nevada_sample.osm", "r")
post_code_re=re.compile(r'(^(89)\d{3}$)|(^(89)\d{3}-\d{4}$)')
post_code_re_NV=re.compile(r'^(NV)\s(89)\d{3}$')
post_code_re_Nevada=re.compile(r'(Nevada)\s(89)\d{3}')

def audit_postcode(post_codes, postcode):
    m=post_code_re.search(postcode)
    NV_abbr=post_code_re_NV.search(postcode)
    NV_full=post_code_re_Nevada.search(postcode)
    if m:
        post_code_group=m.group()
        if post_code_group not in post_codes:
            post_codes[post_code_group].add(postcode)
    elif NV_abbr:
        post_code_group=NV_abbr.group()
        if post_code_group not in post_codes:
            post_codes['NV_abbr'].add(postcode)
    elif NV_full:
        post_code_group=NV_full.group()
        if post_code_group not in post_codes:
            post_codes['NV_full'].add(postcode)
    else:
        post_codes['unknown'].add(postcode)

def is_postcode(elem):
        return (elem.attrib['k']=="addr:postcode")

def postcode_audit(osm_file):
    post_codes=defaultdict(set)
    for event, elem in ET.iterparse(osm_file,events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postcode(tag):
                    audit_postcode(post_codes, tag.attrib['v'])    
    osm_file.close()
    return post_codes

def update_postcode(postcode):
    m=post_code_re.search(postcode)
    NV_abbr=post_code_re_NV.search(postcode)
    NV_full=post_code_re_Nevada.search(postcode)
    if m:
        return m.group()
    elif NV_abbr:
        NV_abbr_group=NV_abbr.group()
        # print NV_abbr_group
        return NV_abbr_group[3:]
    elif NV_full:
        NV_full_group=NV_full.group()
        # print NV_full_group
        return NV_full_group[7:]
    else:
        return "NOT CORRECT POSTCODE"

def updated_postcode(elem):
    updated_name=update_postcode(elem.attrib['v'])
    return updated_name
    
def test():
    post_codes_set=postcode_audit(osm_file)
    # pprint.pprint(dict(post_codes_set))
    
    for post_code,ways in post_codes_set.iteritems():
        for name in ways:
            better_name=update_postcode(name)
            print name,"=>",better_name

if __name__=='__main__':
    test()



# In[ ]:




