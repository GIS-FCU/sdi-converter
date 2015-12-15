#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Superbil'
__version__ = '0.1.0'

import shapefile

sf = shapefile.Reader("shapefiles/路網數值圖103年_西屯區道路路段")

# 確認 shapeType 種類
if sf.shapeType is 3:
    print("PolyLine")
    # srs = sf.shapeRecords()
    mapping = {}
    index = 0
    for f in sf.fields:
        # 跳過第 0 個這個不是 field
        if index is not 0:
            key = f[0]
            mapping[key] = index
        index = index + 1

    print(mapping)
