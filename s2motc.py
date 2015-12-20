#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Superbil'
__version__ = '0.1.0'

import shapefile
import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)
sf = shapefile.Reader("shapefiles/路網數值圖103年_西屯區道路路段")

# 確認 shapeType 種類
if sf.shapeType is 3:
    log.debug("PolyLine")
    # srs = sf.shapeRecords()
    mapping = {}
    index = 0
    for f in sf.fields:
        if index is not 0:
            key = f[0]
            mapping[key] = index - 1
        index = index + 1
    log.debug(mapping)

    # 抓特定道路名稱
    l = list()
    for r in sf.records():
        n = r[mapping['roadname']]
        if "台12" in str(n):
            l.append(r)
    log.debug(l)
