import geoalchemy2 as gsa
import sqlalchemy as sa
from shapely.geometry import shape
from sqlalchemy_utils.types.choice import ChoiceType

from .database import Base


def geom_init_decorator(cls):
    init = cls.__init__

    def new_init(self, *args, geom, **kwargs):
        if isinstance(geom, dict):
            geom = gsa.shape.from_shape(shape(geom), srid=4326)
        init(self, *args, geom=geom, **kwargs)

    @property
    def geometry(self):
        shape = gsa.shape.to_shape(self.geom)
        return shape.__geo_interface__

    cls.geometry = geometry
    cls.__init__ = new_init
    return cls


class User(Base):
    __tablename__ = "users"

    ROLE_TYPES = [(1, "admin"), (2, "user")]

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    username = sa.Column(sa.String(32), unique=True, index=True)
    hashed_password = sa.Column(sa.String)
    full_name = sa.Column(sa.String(64), nullable=True)
    role = sa.Column(
        ChoiceType(ROLE_TYPES, impl=sa.Integer()), default=2, nullable=False
    )
    created_at = sa.Column(sa.DateTime, server_default=sa.sql.func.now())

    def __repr__(self):
        return f"User(id={self.id},username={self.username})"


class District_property(Base):
    __tablename__ = "district_properties"

    district_id = sa.Column(
        sa.ForeignKey("districts.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    common_area = sa.Column(sa.Float, nullable=False)
    beers_per_square_km = sa.Column(sa.Float)
    shop_numbers = sa.Column(sa.Integer)
    green_area = sa.Column(sa.Float)
    station_numbers = sa.Column(sa.Integer)
    avg_altitude_apartments = sa.Column(sa.Float)
    garage_area = sa.Column(sa.Float)
    retail_area = sa.Column(sa.Float)

    @property
    def title(self) -> str:
        return self.district.title

    district = sa.orm.relationship("District", back_populates="properties")


class Block_property(Base):
    __tablename__ = "block_properties"

    block_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("blocks.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    common_area = sa.Column(sa.Float, nullable=False)
    beers_per_square_km = sa.Column(sa.Float)
    shop_numbers = sa.Column(sa.Integer)
    green_area = sa.Column(sa.Float)
    station_numbers = sa.Column(sa.Integer)
    avg_altitude_apartments = sa.Column(sa.Float)
    garage_area = sa.Column(sa.Float)
    retail_area = sa.Column(sa.Float)

    @property
    def title(self) -> str:
        return self.block.title

    block = sa.orm.relationship("Block", back_populates="properties")


class City_property(Base):
    __tablename__ = "city_properties"

    city_id = sa.Column(
        sa.ForeignKey("cities.id", ondelete="CASCADE"), primary_key=True, index=True
    )

    @property
    def title(self) -> str:
        return self.district.title

    city = sa.orm.relationship("City", back_populates="properties")


@geom_init_decorator
class District(Base):
    __tablename__ = "districts"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String, nullable=False)
    city_id = sa.Column(sa.ForeignKey("cities.id", ondelete="CASCADE"))
    geom = sa.Column(
        gsa.Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False
    )

    city = sa.orm.relationship("City", back_populates="districts", lazy="selectin")
    properties = sa.orm.relationship(
        "District_property", back_populates="district", uselist=False, lazy="selectin"
    )


@geom_init_decorator
class Block(Base):
    __tablename__ = "blocks"
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String, nullable=False)
    city_id = sa.Column(sa.ForeignKey("cities.id", ondelete="CASCADE"))
    geom = sa.Column(
        gsa.Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False
    )

    city = sa.orm.relationship("City", back_populates="blocks", lazy="selectin")
    properties = sa.orm.relationship(
        "Block_property", back_populates="block", uselist=False, lazy="selectin"
    )


@geom_init_decorator
class City(Base):
    __tablename__ = "cities"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String(120), nullable=False)
    geom = sa.Column(
        gsa.Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False
    )

    districts = sa.orm.relationship("District", back_populates="city", lazy="selectin")
    blocks = sa.orm.relationship("Block", back_populates="city", lazy="selectin")
    properties = sa.orm.relationship(
        "City_property", back_populates="city", uselist=False, lazy="selectin"
    )
