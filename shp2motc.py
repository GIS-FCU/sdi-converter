#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Superbil'
__version__ = '0.3.0'

import sys
import logging
import xml.etree.ElementTree as ET

import shapefile

log = logging.getLogger()
# log.setLevel(logging.DEBUG)

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

def setRefered(sf, mapping, root, r):
    # net:ReferedProperty
    referedProperty = ET.SubElement(root, 'net:ReferedProperty')
    rID = ET.SubElement(referedProperty, 'ro:RoadIdentity')

    n = ET.SubElement(rID, "ro:roadName")
    n.text = str(r[mapping['roadname']])

    # rc = ET.SubElement(rID, "ro:roadCode")
    # rc.text = str(r[mapping['roadcode']])

    roadType = ET.SubElement(rID, "ro:roadClass")
    roadType.text = str(r[mapping['roadtype']])

    # roadaliasn = ET.SubElement(rID, "ro:roadAliasName")
    # roadaliasn.text = str(r[mapping['roadaliasn']])
    return referedProperty

def setLink(sf, mapping, root, rec, point, counter):
    link = ET.SubElement(root, 'net:link')
    link.set('xlink:type', 'simple')
    rlink = ET.SubElement(link, 'ro:RoadLink')

    trival = ET.SubElement(rlink, 'ro:trival')
    trival.text = 'false'

    rStruct = ET.SubElement(rlink, 'ro:structureType')
    rStruct.text = rec[mapping['roadstruct']]

    rLinkID = ET.SubElement(rlink, 'ro:roadLinkID')
    rLinkID.text = "{}-{}".format(rec[mapping['roadid']], rec[mapping['roadcomnum']])

    rID = ET.SubElement(root, 'ro:roadID')
    rID.text = rec[mapping['roadid']]

    nGeo = ET.SubElement(rlink, 'net:geometry')
    nGeo.set('xlink:type', 'simple')
    # 線段的 GML
    addPoint(nGeo, 'epsg:3826', point)

    rStartNode = ET.SubElement(rlink, 'net:startNode')
    setRoadNode(rStartNode, rec[mapping['fnode']])
    rEndNode = ET.SubElement(rlink, 'net:endNode')
    setRoadNode(rEndNode, rec[mapping['tnode']])

def setRoadNode(e, t):
    rn = ET.SubElement(e, 'ro:RoadNode')
    ri = ET.SubElement(rn, 'ro:roadNodeID')
    ri.text = t

def addPoint(e, srsName, points):
    lineElement = ET.SubElement(e, 'gml:LineString')
    lineElement.set('srsName', srsName)
    posElement = ET.SubElement(lineElement, 'gml:posList')
    posElement.text = "{} {} {} {}".format(points[0][0], points[0][1], points[1][0], points[1][1])

def main():
    sf = shapefile.Reader("shapefiles/路網數值圖103年_西屯區道路路段")

    # 確認 shapeType 種類
    if sf.shapeType is 3:
        log.debug("PolyLine")
        root = ET.Element('ro:Road')
        m = create_mapping(sf.fields)
        log.debug(m)

        index = 0
        rp = None
        shapes = sf.shapes()
        for rec in sf.iterRecords():
            if "台12" == rec[m['roadname']]:
                if rp is None:
                    rp = setRefered(sf, m, root, rec)

                setLink(sf, m, root, rec, shapes[index].points, index)
                index = index + 1

        log.debug(ET.dump(root))

        tree = ET.ElementTree(root)
        with open ('台12motc.xml', 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            tree.write(f, encoding="unicode")

if __name__ == '__main__':
    main()
