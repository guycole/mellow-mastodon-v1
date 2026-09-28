#
# Title: postgres.py
# Description: postgresql support
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import datetime
import logging

from typing import Any

import sqlalchemy
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import desc

from helper.sql_table import (
    DailyScore,
    GeoLoc,
    LoadLog,
    Observation,
    PeakerScore,
)

logger = logging.getLogger("postgres")


class PostGres:
    db_engine = None
    Session = None

    def __init__(self, session: sqlalchemy.orm.session.sessionmaker):
        self.Session = session

    def _normalize_task(self, args: dict[str, Any]) -> dict[str, Any]:
        candidate = dict(args)
        task = candidate.get("task")
        if isinstance(task, str):
            task = task.strip()

        if not task:
            raise ValueError("task must be a non-empty string")

        candidate["task"] = task

        return candidate

    def daily_score_insert_or_update(self, args: dict[str, Any]) -> DailyScore:
        args = self._normalize_task(args)
        candidate = DailyScore(args)

        try:
            with self.Session() as session:
                existing = session.scalars(
                    select(DailyScore).filter(
                        and_(
                            DailyScore.crate_name == candidate.crate_name,
                            DailyScore.score_date == candidate.score_date,
                            DailyScore.host_name == candidate.host_name,
                            DailyScore.task == candidate.task,
                        )
                    )
                ).first()

                if existing is None:
                    session.add(candidate)
                else:
                    existing.file_quantity += candidate.file_quantity
                    existing.peaker_quantity += candidate.peaker_quantity

                session.commit()
        except Exception as error:
            logger.exception("daily_score_insert_or_update failed: %s", error)

        return candidate

    def geo_loc_select_by_site(self, site_name: str) -> list[GeoLoc]:
        statement = (
            select(GeoLoc)
            .filter_by(site_name=site_name)
            .order_by(desc(GeoLoc.fix_time), desc(GeoLoc.id))
        )

        with self.Session() as session:
            return session.scalars(statement).all()

    def load_log_insert(self, args: dict[str, Any]) -> LoadLog:
        args = self._normalize_task(args)
        candidate = LoadLog(args)

        try:
            with self.Session() as session:
                session.add(candidate)
                session.commit()
        except Exception as error:
            logger.exception("load_log_insert failed: %s", error)

        return candidate

    def load_log_select_all(self) -> list[LoadLog]:
        with self.Session() as session:
            return session.scalars(
                select(LoadLog).order_by(desc(LoadLog.load_time), desc(LoadLog.id))
            ).all()

    def load_log_select_all_by_date(self, target: datetime.date) -> list[LoadLog]:
        with self.Session() as session:
            return session.scalars(
                select(LoadLog)
                .filter(func.date(LoadLog.load_time) == target)
                .order_by(desc(LoadLog.load_time), desc(LoadLog.id))
            ).all()

    def load_log_select_by_file_name(self, file_name: str) -> LoadLog | None:
        with self.Session() as session:
            return session.scalars(
                select(LoadLog).filter_by(file_name=file_name)
            ).first()

    def observation_insert(self, args: dict[str, Any]) -> Observation:
        candidate = Observation(args)

        try:
            with self.Session() as session:
                session.add(candidate)
                session.commit()
        except Exception as error:
            logger.exception("observation_insert failed: %s", error)

        return candidate

    def peaker_score_insert_or_update(self, args: dict[str, Any]) -> PeakerScore:
        args = self._normalize_task(args)
        candidate = PeakerScore(args)

        try:
            with self.Session() as session:
                existing = session.scalars(
                    select(PeakerScore).filter(
                        and_(
                            PeakerScore.crate_name == candidate.crate_name,
                            PeakerScore.freq_hz == candidate.freq_hz,
                            PeakerScore.task == candidate.task,
                        )
                    )
                ).first()

                if existing is None:
                    session.add(candidate)
                else:
                    existing.peaker_quantity += 1

                session.commit()
        except Exception as error:
            logger.exception("peaker_score_insert_or_update failed: %s", error)

        return candidate

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
