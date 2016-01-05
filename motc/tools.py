#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def create_mapping(fields):
    mapping = {}
    index = 0
    for f in fields:
        if index is not 0:
            key = f[0]
            mapping[key] = index - 1
        index = index + 1
    return mapping
