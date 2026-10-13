#
# Title: sql_table.py
# Description: database table definitions
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
# import sqlalchemy
# from sqlalchemy import and_
# from sqlalchemy import select

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    SmallInteger,
    String,
)

from sqlalchemy.orm import registry
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.declarative import declared_attr

mapper_registry = registry()


class Base(DeclarativeBase):
    pass


class Equipment(Base):
    """equipment table definition"""

    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True)
    antenna = Column(String)
    note = Column(String)
    project = Column(String)
    receiver = Column(String)

    def __init__(self, args: dict[str, any]):
        self.antenna = args["antenna"]
        self.note = args["note"]
        self.project = args["project"]
        self.receiver = args["receiver"]

    def __repr__(self):
        return f"equipment({self.project})"


class LoadLog(Base):
    """load_log table definition"""

    __tablename__ = "load_log"

    id = Column(Integer, primary_key=True)
    file_name = Column(String)
    population = Column(Integer)
    project = Column(String)
    time_stamp_epoch = Column(BigInteger)
    equipment_id = Column(BigInteger)
    schema_version = Column(SmallInteger)
    site_id = Column(BigInteger)

    def __init__(self, args: dict[str, any]):
        self.file_name = args["file_name"]
        self.time_stamp_epoch = args["time_stamp_epoch"]
        self.population = args["population"]
        self.project = args["project"]
        self.equipment_id = args["equipment_id"]
        self.schema_version = args["schema_version"]
        self.site_id = args["site_id"]

    def __repr__(self):
        return f"load_log({self.file_name} {self.time_stamp_epoch})"


class Observation(Base):
    """observation table definition"""

    __tablename__ = "observation"

    id = Column(Integer, primary_key=True)
    freq_hz = Column(Integer)
    load_log_id = Column(BigInteger)
    rolling_mean = Column(Float)
    signal_dbm = Column(Float)

    def __init__(self, args: dict[str, any]):
        self.freq_hz = args["freq_hz"]
        self.load_log_id = args["load_log_id"]
        self.rolling_mean = args["rolling_mean"]
        self.signal_dbm = args["signal_dbm"]

    def __repr__(self):
        return f"observation({self.freq_hz} {self.signal_dbm} {self.load_log_id})"


class Population(Base):
    """population table definition"""

    __tablename__ = "population"

    id = Column(Integer, primary_key=True)
    case_uuid = Column(String)
    freq_hz = Column(Integer)
    obs_first = Column(DateTime)
    obs_last = Column(DateTime)
    population = Column(BigInteger)
    site_id = Column(BigInteger)
    note = Column(String)

    def __init__(self, args: dict[str, any]):
        self.freq_hz = args["freq_hz"]
        self.case_uuid = args["case_uuid"]
        self.note = args["note"]
        self.obs_first = args["obs_first"]
        self.obs_last = args["obs_last"]
        self.population = args["population"]
        self.site_id = args["site_id"]

    def __repr__(self):
        return f"population({self.site_id} {self.freq_hz} {self.population})"


class Site(Base):
    """site table definition"""

    __tablename__ = "site"

    id = Column(Integer, primary_key=True)
    altitude = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    name = Column(String)
    note = Column(String)

    def __init__(self, args: dict[str, any]):
        self.altitude = args["altitude"]
        self.latitude = args["latitude"]
        self.longitude = args["longitude"]
        self.name = args["name"]
        self.note = args["note"]

    def __repr__(self):
        return f"site({self.name})"


# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
