#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Superbil'
__version__ = '0.2.0'

import sys
import logging
import xml.etree.ElementTree as ET

import shapefile

def create_mapping(fields):
    mapping = {}
    index = 0
    for f in fields:
        if index is not 0:
            key = f[0]
            mapping[key] = index - 1
        index = index + 1
    log.debug(mapping)
    return mapping

def setElement(sf, mapping, root):
    # net:ReferedProperty
    referedProperty = ET.SubElement(root, 'net:ReferedProperty')
    rID = ET.SubElement(referedProperty, 'ro:RoadIdentity')

    n = ET.SubElement(rID, "ro:roadName")
    n.text = str(r[m['roadname']])

    # rc = ET.SubElement(rID, "ro:roadCode")
    # rc.text = str(r[m['roadcode']])

    roadType = ET.SubElement(rID, "ro:roadClass")
    roadType.text = str(r[m['roadtype']])

    # roadaliasn = ET.SubElement(rID, "ro:roadAliasName")
    # roadaliasn.text = str(r[m['roadaliasn']])

    link = ET.SubElement(root, 'net:link')
    link.set('xlink:type', 'simple')
    rlink = ET.SubElement(link, 'ro:RoadLink')

    nGeo = ET.SubElement(rlink, 'net:geometry')
    nGeo.set('xlink:type', 'simple')

    trival = ET.SubElement(rlink, 'ro:trival')
    trival.text = 'false'

    rStruct = ET.SubElement(rlink, 'ro:structureType')
    rStruct.text = r[m['roadstruct']]

    rLinkID = ET.SubElement(rlink, 'ro:roadLinkID')
    rLinkID.text = "{}-{}".format(r[m['roadid']], r[m['roadcomnum']])

    rID = ET.SubElement(root, 'ro:roadID')
    rID.text = r[m['roadid']]

log = logging.getLogger()
# log.setLevel(logging.DEBUG)
sf = shapefile.Reader("shapefiles/路網數值圖103年_西屯區道路路段")

# 確認 shapeType 種類
if sf.shapeType is 3:
    log.debug("PolyLine")
    root = ET.Element('ro:Road')
    m = create_mapping(sf.fields)
    log.debug(m)

    for r in sf.records():
        setElement(sf, m, root)
        break

    log.debug(ET.dump(root))

    sys.stdout.write('<?xml version="1.0" ?>\n')
    ET.dump(root)
