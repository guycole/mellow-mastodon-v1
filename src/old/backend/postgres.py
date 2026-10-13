#
# Title: postgres.py
# Description: postgresql support
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#

import datetime
import time

import sqlalchemy
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import select

from sql_table import Equipment, LoadLog, Observation, Population, Site


class PostGres:
    db_engine = None
    Session = None

    def __init__(self, session: sqlalchemy.orm.session.sessionmaker):
        self.Session = session

    def equipment_select(self, antenna: str, project: str, receiver: str) -> Equipment:
        with self.Session() as session:
            return session.scalars(
                select(Equipment).filter_by(
                    antenna=antenna,
                    project=project,
                    receiver=receiver,
                )
            ).first()

    def load_log_insert(self, args: dict[str, any]) -> LoadLog:
        candidate = LoadLog(args)

        try:
            with self.Session() as session:
                session.add(candidate)
                session.commit()
        except Exception as error:
            print(error)

        return candidate

    def load_log_select_by_file_name(self, file_name: str) -> LoadLog:
        with self.Session() as session:
            return session.scalars(
                select(LoadLog).filter_by(file_name=file_name)
            ).first()

    def observation_insert(self, args: dict[str, any]) -> Observation:
        candidate = Observation(args)

        try:
            with self.Session() as session:
                session.add(candidate)
                session.commit()
        except Exception as error:
            print(error)

        return candidate

    def population_insert(self, args: dict[str, any]) -> Population:
        candidate = Population(args)

        try:
            with self.Session() as session:
                session.add(candidate)
                session.commit()
        except Exception as error:
            print(error)

        return candidate

    def population_select_all_by_site(self, site_id: int) -> list[Site]:
        statement = (
            select(Population).filter_by(site_id=site_id).order_by(Population.freq_hz)
        )

        with self.Session() as session:
            return session.scalars(statement).all()

    def population_select_by_frequency(self, freq_hz: int) -> list[Population]:
        with self.Session() as session:
            return session.scalars(select(Population).filter_by(freq_hz=freq_hz)).all()

    def population_select_by_frequency_site_id(
        self, freq_hz: int, site_id: int
    ) -> list[Population]:
        with self.Session() as session:
            return session.scalars(
                select(Population).filter_by(freq_hz=freq_hz, site_id=site_id)
            ).all()

    def population_select_by_id(self, id: int) -> Population:
        with self.Session() as session:
            return session.scalars(select(Population).filter_by(id=id)).first()

    def population_update(self, candidate: Population) -> None:
        try:
            with self.Session() as session:
                session.add(candidate)
                session.commit()
        except Exception as error:
            print(error)

    def site_select_all(self) -> list[Site]:
        statement = select(Site)

        with self.Session() as session:
            return session.scalars(statement).all()

    def site_select_by_id(self, id: int) -> Site:
        with self.Session() as session:
            return session.scalars(select(Site).filter_by(id=id)).first()

    def site_select_by_name(self, name: str) -> Site:
        with self.Session() as session:
            return session.scalars(select(Site).filter_by(name=name)).first()


# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
