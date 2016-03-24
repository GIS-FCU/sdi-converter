#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Superbil'
__version__ = '0.2.4'

from motc import tools
import argparse
import datetime
import sys
import time
from tqdm import tqdm
import pymssql
import shapefile

CREATE_TABLE_ROAD = """
CREATE TABLE [dbo].[tblRoad](
        [PID] [int] IDENTITY(1,1) NOT NULL,
        [RoadID] [varchar](30) NOT NULL,
        [RoadName] [nvarchar](20) NOT NULL,
        [RoadClass] [varchar](5) NOT NULL,
        [RoadCode] [varchar](10) NULL,
        [RoadAliasName] [nvarchar](20) NULL,
        [LaneName] [nvarchar](10) NULL,
        [AlleyName] [nvarchar](10) NULL,
        [CreateTime] [datetime] NOT NULL,
 CONSTRAINT [PK_tblRoad] PRIMARY KEY CLUSTERED
(
        [PID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
"""

CREATE_TABLE_ROADLINK = """
CREATE TABLE [dbo].[tbRoadLink](
        [PID] [int] IDENTITY(1,1) NOT NULL,
        [RoadLinkID] [varchar](20) NOT NULL,
        [RoadName] [nvarchar](20) NOT NULL,
        [RoadClass] [varchar](5) NOT NULL,
        [RoadCode] [varchar](10) NULL,
        [StartRoadID] [varchar](20) NULL,
        [EndRoadID] [varchar](20) NULL,
        [StructureType] [int] NOT NULL,
        [BridgeID] [nvarchar](20) NULL,
        [TunnelID] [nvarchar](20) NULL,
        [Width] [nvarchar](20) NULL,
        [AliasName] [nvarchar](20) NULL,
        [Address_County] [nvarchar](10) NULL,
        [Address_RoadName] [nvarchar](20) NULL,
        [ModifiedDate] [datetime] NOT NULL,
        [TrafficDirection] [nvarchar](10) NULL,
        [Geometry] [geometry] NOT NULL,
        [UpdateTime] [datetime] NOT NULL,
 CONSTRAINT [PK_tbRoadLink] PRIMARY KEY CLUSTERED
(
        [PID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
"""


def insertRoad(conn, sf, mapping):
    cursor = conn.cursor()
    for rec in tqdm(sf.iterRecords(), total=len(sf.records())):
        d = datetime.datetime.now()
        cursor.executemany("""
        INSERT INTO tblRoad (RoadID, RoadName, RoadClass, RoadCode, RoadAliasName, CreateTime)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, [(
            rec[mapping['roadid']][:30],      # RoadID
            rec[mapping['roadname']][:20],    # RoadName
            rec[mapping['roadtype']][:5],     # RoadClass
            rec[mapping['roadcode']][:10],    # RoadCode
            rec[mapping['roadaliasn']][:20],  # RoadAliasName
            d.strftime('%Y-%m-%d %H:%M:%S'),  # CreateTime
            )])
        conn.commit()


def insertRoadLink(conn, sf, mapping):
    cursor = conn.cursor()
    i = 0
    shapes = sf.shapes()
    for rec in tqdm(sf.iterRecords(), total=len(sf.records())):
        # updatedate will like 110829, must change to datetime
        mdStr = "20{}".format(rec[mapping['updatedate']])
        md = datetime.datetime.fromtimestamp(time.mktime(time.strptime(mdStr, "%Y%m%d")))
        ud = datetime.datetime.now()
        l = []
        for p in shapes[i].points:
            l.append("{} {}".format(p[0], p[1]))
        g = "LineString({})".format(', '.join(l))
        cursor.executemany("""
        INSERT INTO tbRoadLink (
        RoadLinkID,
        RoadName,
        RoadClass,
        RoadCode,
        StartRoadID,
        EndRoadID,
        StructureType,
        BridgeID,
        TunnelID,
        Width,
        AliasName,
        Address_County,
        ModifiedDate,
        TrafficDirection,
        Geometry,
        UpdateTime
        ) VALUES (%s, %s, %s, %s, %d, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [(
            rec[mapping['roadid']],                                         # RoadLinkID
            rec[mapping['roadname']][:20],                                  # RoadName
            rec[mapping['roadtype']][:5],                                   # RoadClass
            rec[mapping['roadcode']][:10],                                  # RoadCode
            rec[mapping['fnode']][:20],                                     # StartRoadID
            rec[mapping['tnode']][:20],                                     # EndRoadID
            rec[mapping['roadstruct']],                                     # StructureType
            rec[mapping['bridgeid']][:20],                                  # BridgeID
            rec[mapping['tunnelid']][:20],                                  # TunnelID
            rec[mapping['width']],                                          # Width
            rec[mapping['rdaliasn']][:20] if 'rdaliasn' in mapping else '', # AliasName
            'B',                                                            # Address_County
            md.strftime('%Y-%m-%d %H:%M:%S'),                               # ModifiedDate
            rec[mapping['dir']],                                            # TrafficDirection
            g,                                                              # Geometry
            ud.strftime('%Y-%m-%d %H:%M:%S'),                               # UpdateTime
            )])
        conn.commit()
        i = i + 1


def checkTable(conn, tableName):
    coursor = conn.cursor()
    d = datetime.datetime.now()
    newTableName = "{0}_{1}".format(tableName, d.strftime('%Y%m%d%H%M'))
    pkTable = "PK_{}".format(tableName)
    newPKTable = "{}_{}".format(pkTable, d.strftime('%Y%m%d%H%M'))
    coursor.executemany("""
    IF EXISTS( SELECT * FROM information_schema.tables WHERE table_name = %s )
    BEGIN
        EXEC sp_rename %s, %s
        EXEC sp_rename %s, %s
    END
    """, [(tableName, tableName, newTableName, pkTable, newPKTable)])
    conn.commit()


def main():
    shapefileName = "shapefiles/路網數值圖103年_西屯區道路路段"
    sys.stdout.write("Start read shapefile {}\n".format(shapefileName))
    sf = shapefile.Reader(shapefileName)
    m = tools.create_mapping(sf.fields)

    parser = argparse.ArgumentParser()
    parser.add_argument('server', help='server ip')
    parser.add_argument('username', help='user name')
    parser.add_argument('password', help='user password')
    parser.add_argument('database', help='database name')
    args = parser.parse_args()

    conn = pymssql.connect(args.server, args.username, args.password, args.database)
    sys.stdout.write("Start connect to server\n")
    cursor = conn.cursor()

    sys.stdout.write("Check table is existed\n")
    checkTable(conn, "tbRoadLink")

    sys.stdout.write("Create table\n")
    cursor.execute(CREATE_TABLE_ROADLINK)

    sys.stdout.write("Start insert RoadLink\n")
    insertRoadLink(conn, sf, m)

    sys.stdout.write("Finish all\n")
    conn.close()

if __name__ == '__main__':
    main()
