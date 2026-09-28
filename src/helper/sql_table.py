#
# Title: sql_table.py
# Description: database table definitions
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
from datetime import datetime
from typing import Any

from sqlalchemy import Column
from sqlalchemy import BigInteger, Date, DateTime, Float, Integer, SmallInteger, String

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import registry

mapper_registry = registry()


class Base(DeclarativeBase):
    pass


class DailyScore(Base):
    __tablename__ = "mastodon_daily_score"

    id = Column(BigInteger, primary_key=True)
    crate_name = Column(String)
    file_quantity = Column(Integer)
    host_name = Column(String)
    peaker_quantity = Column(Integer)
    score_date = Column(Date)
    task = Column(String)

    def __init__(self, args: dict[str, Any]):
        self.crate_name = args["crate_name"]
        self.file_quantity = args["file_quantity"]
        self.host_name = args["host_name"]
        self.peaker_quantity = args["peaker_quantity"]
        self.score_date = args["score_date"]
        self.task = args["task"]

    def __repr__(self):
        return f"daily_score({self.score_date} {self.host_name})"


class GeoLoc(Base):
    __tablename__ = "mastodon_geo_loc"

    id = Column(BigInteger, primary_key=True)
    altitude = Column(Float)
    course = Column(Float)
    fix_time = Column(DateTime)
    host_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    site_name = Column(String)
    speed = Column(Float)

    def __init__(self, args: dict[str, Any]):
        self.altitude = args["altitude"]
        self.course = args["course"]
        self.fix_time = args.get("fix_time", datetime.now())
        self.host_name = args["host_name"]
        self.latitude = args["latitude"]
        self.longitude = args["longitude"]
        self.site_name = args["site_name"]
        self.speed = args["speed"]

    def __repr__(self):
        return f"geo_loc({self.site_name} {self.host_name})"


class LoadLog(Base):
    __tablename__ = "mastodon_load_log"

    id = Column(BigInteger, primary_key=True)
    crate_name = Column(String)
    epoch_seconds = Column(BigInteger)
    file_name = Column(String)
    geo_loc_id = Column(BigInteger)
    host_name = Column(String)
    load_time = Column(DateTime)
    mode = Column(String)
    obs_time = Column(DateTime)
    peaker_quantity = Column(SmallInteger)
    site_name = Column(String)
    source_file_name = Column(String)
    task = Column(String)

    def __init__(self, args: dict[str, Any]):
        self.crate_name = args["crate_name"]
        self.epoch_seconds = args["epoch_seconds"]
        self.file_name = args["file_name"]
        self.geo_loc_id = args["geo_loc_id"]
        self.host_name = args["host_name"]
        self.load_time = args.get("load_time", datetime.now())
        self.mode = args["mode"]
        self.obs_time = args["obs_time"]
        self.peaker_quantity = args["peaker_quantity"]
        self.site_name = args["site_name"]
        self.source_file_name = args["source_file_name"]
        self.task = args["task"]

    def __repr__(self):
        return f"load_log({self.file_name} {self.obs_time} {self.task} {self.host_name})"


class Observation(Base):
    """observation table definition"""

    __tablename__ = "mastodon_observation"

    id = Column(BigInteger, primary_key=True)
    baseline_dbm = Column(Float)
    freq_hz = Column(Integer)
    load_log_id = Column(BigInteger)
    power_dbm = Column(Float)

    def __init__(self, args: dict[str, Any]):
        self.baseline_dbm = args["baseline_dbm"]
        self.freq_hz = args["freq_hz"]
        self.load_log_id = args["load_log_id"]
        self.power_dbm = args["power_dbm"]

    def __repr__(self):
        return f"observation({self.load_log_id} {self.freq_hz} {self.baseline_dbm} {self.power_dbm})"


class PeakerScore(Base):
    __tablename__ = "mastodon_peaker_score"

    id = Column(BigInteger, primary_key=True)
    crate_name = Column(String)
    freq_hz = Column(Integer)
    peaker_quantity = Column(Integer)
    task = Column(String)

    def __init__(self, args: dict[str, Any]):
        self.crate_name = args["crate_name"]
        self.freq_hz = args["freq_hz"]
        self.peaker_quantity = args["peaker_quantity"]
        self.task = args["task"]

    def __repr__(self):
        return f"peaker_score({self.freq_hz} {self.peaker_quantity})"

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
