#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Superbil'
__version__ = '0.1.0'

from os import getenv
from motc import tools
import datetime
import argparse
import pymssql
import shapefile

CREATE_TABLE = """
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
    for rec in sf.iterRecords():
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
    for rec in sf.iterRecords():
        md = datetime.datetime.fromtimestamp(int(rec[mapping['updatedate']]))
        ud = datetime.datetime.now()
        g = "LineString({} {}, {} {})".format(
            shapes[i].points[0][0],
            shapes[i].points[0][1],
            shapes[i].points[1][0],
            shapes[i].points[1][1]
        )
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
            tools.create_RoadLink(rec[mapping['roadid']], rec[mapping['roadcomnum']]), # RoadLinkID
            rec[mapping['roadname']][:20],                                             # RoadName
            rec[mapping['roadtype']][:5] ,                                             # RoadClass
            rec[mapping['roadcode']][:10].decode('utf-8') ,                            # RoadCode
            rec[mapping['fnode']][:20],                                                # StartRoadID
            rec[mapping['tnode']][:20],                                                # EndRoadID
            rec[mapping['roadstruct']],                                                # StructureType
            rec[mapping['bridgeid']][:20].decode('utf-8'),                             # BridgeID
            rec[mapping['tunnelid']][:20].decode('utf-8') ,                            # TunnelID
            rec[mapping['width']],                                                     # Width
            rec[mapping['rdaliasn']][:20] if 'rdaliasn' in mapping else '',            # AliasName
            'B',                                                                       # Address_County
            md.strftime('%Y-%m-%d %H:%M:%S'),                                          # ModifiedDate
            rec[mapping['dir']],                                                       # TrafficDirection
            g,                                                                         # Geometry
            ud.strftime('%Y-%m-%d %H:%M:%S'),                                          # UpdateTime
            )])
        conn.commit()
        i = i + 1


def checkTable(conn, tableName):
    coursor = conn.cursor()
    d = datetime.datetime.now()
    newTableName = "{0}_{1}".format(tableName, d.strftime('%Y%m%d%H%M'))
    coursor.executemany("""
    IF EXISTS( SELECT * FROM information_schema.tables WHERE table_name = %s )
    BEGIN
        EXEC sp_rename %s, %s
    END
    """
        , [(tableName, tableName, newTableName)])
    conn.commit()


def main():
    sf = shapefile.Reader("shapefiles/路網數值圖103年_西屯區道路路段")
    m = tools.create_mapping(sf.fields)

    parser = argparse.ArgumentParser()
    parser.add_argument('server', help='server ip')
    parser.add_argument('username', help='user name')
    parser.add_argument('password', help='user password')
    parser.add_argument('database', help='database name')
    args = parser.parse_args()

    conn = pymssql.connect(args.server, args.username, args.password, args.database)
    cursor = conn.cursor()

    checkTable(conn, "tblRoad")
    checkTable(conn, "tbRoadLink")
    cursor.execute(CREATE_TABLE)

    insertRoad(conn, sf, m)
    insertRoadLink(conn, sf, m)

    # Finish all
    conn.close()

if __name__ == '__main__':
    main()
