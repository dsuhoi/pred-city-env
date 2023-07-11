import random

import sqlalchemy as sa
from geopy.distance import distance as geodist

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    username = sa.Column(sa.String, unique=True, index=True)
    hashed_password = sa.Column(sa.String)
    full_name = sa.Column(sa.String, nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.sql.func.now())

    def __repr__(self):
        return f"User(id={self.id},username={self.username})"


class Location(Base):
    __tablename__ = "locations"
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    zip = sa.Column(sa.Integer, unique=True, index=True, nullable=False)
    city = sa.Column(sa.String(32), nullable=False)
    state_name = sa.Column(sa.Text, nullable=False)
    lat = sa.Column(sa.Float, nullable=False)
    lng = sa.Column(sa.Float, nullable=False)

    @property
    def coords(self) -> (float, float):
        return (self.lat, self.lng)

    def distance(self, loc: "Location") -> float:
        return round(geodist(self.coords, loc.coords).miles, 4)

    def __str__(self):
        return f"zip[{self.lat}, {self.lng}]: {self.zip} # {self.city}"
