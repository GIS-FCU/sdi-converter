#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Superbil'
__version__ = '0.1.0'

from os import getenv
from motc import tools
import datetime
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

CREATE TABLE [dbo].[tblRoadLink](
        [PID] [int] IDENTITY(1,1) NOT NULL,
        [RoadLinkID] [varchar](20) NOT NULL,
        [RoadID] [varchar](30) NOT NULL,
        [StartRoadID] [varchar](20) NULL,
        [EndRoadID] [varchar](20) NULL,
        [Trival] [bit] NOT NULL,
        [StructureType] [int] NOT NULL,
        [FormOfRoad] [varchar](20) NULL,
        [BridgeTunnelName] [nvarchar](20) NULL,
        [Geometry] [geometry] NOT NULL,
        [UpdateTime] [datetime] NOT NULL,
 CONSTRAINT [PK_tblRoadLink] PRIMARY KEY CLUSTERED
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
    i = 0
    shapes = sf.shapes()
    for rec in sf.iterShapes():
        d = datetime.datetime.fromtimestamp(int(rec[mapping['updatedate']]))
        g = "geometry::STGeomFromText('MULTIPOINT({} {}, {} {})', 0)".format(
            shapes[i].points[0][0],
            shapes[i].points[0][1],
            shapes[i].points[1][0],
            shapes[i].points[1][1]
        )
        cursor.executemany("""
        INSERT INTO tblRoadLink (RoadLinkID, RoadID, StartRoadID, EndRoadID, StructureType, Geometry, UpdateTime)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, [
            tools.create_RoadLink(rec[mapping['roadid']], rec[mapping['roadcomnum']]),   # RoadLinkID
            rec[mapping['roadid']],           # RoadID
            rec[mapping['fnode']],            # StartRoadID
            rec[mapping['tnode']],            # EndRoadID
            rec[mapping['roadstruct']],       # StructureType
            rec[mapping['']],                 # Geometry
            d.strftime('%Y-%m-%d %H:%M:%S'),  # UpdateTime
            ])
        cursor.commit()
        i = i + 1


def main():
    sf = shapefile.Reader("shapefiles/路網數值圖103年_西屯區道路路段")
    m = tools.create_mapping(sf.fields)

    server = getenv("MSSQL_SERVER")
    user = getenv("MSSQL_USERNAME")
    password = getenv("MSSQL_PASSWORD")
    database = "motc"

    conn = pymssql.connect(server, user, password, database)
    cursor = conn.cursor()

    cursor.execute(CREATE_TABLE)

    insertRoadLink(cursor, sf, m)
    insertRoad(conn, sf, m)

    # Finish all
    conn.close()

if __name__ == '__main__':
    main()
