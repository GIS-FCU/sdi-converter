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

def setRefered(sf, mapping, root):
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

def setLink(sf, mapping, root):
    link = ET.SubElement(root, 'net:link')
    link.set('xlink:type', 'simple')
    rlink = ET.SubElement(link, 'ro:RoadLink')

    trival = ET.SubElement(rlink, 'ro:trival')
    trival.text = 'false'

    rStruct = ET.SubElement(rlink, 'ro:structureType')
    rStruct.text = r[m['roadstruct']]

    rLinkID = ET.SubElement(rlink, 'ro:roadLinkID')
    rLinkID.text = "{}-{}".format(r[m['roadid']], r[m['roadcomnum']])

    rID = ET.SubElement(root, 'ro:roadID')
    rID.text = r[m['roadid']]

    nGeo = ET.SubElement(rlink, 'net:geometry')
    nGeo.set('xlink:type', 'simple')
    # 線段的 GML

    rStartNode = ET.SubElement(rlink, 'net:startNode')
    # setRoadNode(rStartNode, fnode)

    rEndNode = ET.SubElement(rlink, 'net:endNode')
    # setRoadNode(rEndNode, tnode)

def setRoadNode(e, t):
    rn = ET.SubElement(e, 'ro:RoadNode')
    ri = ET.SubElement(rn, 'ro:roadNodeID')
    ri.text = t

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
        if "台12" == r[m['roadname']]:
def addPoint(e, srsName, pointA, pointB):
    lineE = ET.SubElement(e, 'gml:LineString')
    pointElement.set('srsName', srsName)
    posElement = ET.SubElement(lineE, 'gml:posList')
    posElement.text = "{} {} {} {}".format(point[0][0], point[0][1], point[1][0], point[1][1])

            setRefered(sf, m, root)
            break

    log.debug(ET.dump(root))

    sys.stdout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    ET.dump(root)
