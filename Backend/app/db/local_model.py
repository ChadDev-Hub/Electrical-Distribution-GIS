from sqlmodel import Field, SQLModel, Text, Integer, Column, Float, MetaData, Numeric
from typing import Optional
from geoalchemy2 import Geometry

local_metadata = MetaData(schema="gis")
# FRANCHISE AREA
class localFranchiseArea(SQLModel, table=True):
    __tablename__:str = "franchise_area"
    metadata = local_metadata
    id: Optional[int] = Field(default=None, sa_column=Column("id", Integer, primary_key=True))
    geom: Optional[str] = Field(default=None, sa_column=Column("geom",type_=Geometry(geometry_type="POLYGON", srid=4326)))
    village: Optional[str] = Field(default=None, sa_column=Column("village", type_=Text))
    municipality: Optional[str] = Field(default=None, sa_column=Column("municipality", type_=Text))
    description: Optional[str] = Field(default=None, sa_column=Column("description", type_=Text))
    shape_area: Optional[str] = Field(default=None, sa_column=Column("shape_area", type_=Integer))
    status: Optional[str] = Field(default=None, sa_column=Column(name="electricity_status", type_=Text))
#  SUBSTATION
class localSubstation(SQLModel, table=True):
    __tablename__:str = "power_station"
    metadata = local_metadata
    id: Optional[int] = Field(default=None, sa_column=Column("id", Integer, primary_key=True))
    geom: Optional[str] = Field(default=None, sa_column=Column("geom", Geometry("POINT",4326)))
    generator_id:Optional[str] = Field(default=None, sa_column=Column("generator_id", Text))
    phasing: Optional[str] = Field(default=None, sa_column=Column("phasing",Text))
    description: Optional[str] = Field(default=None, sa_column=Column("description", Text))
    generator_type: Optional[str] = Field(default=None, sa_column=Column("generator_type", Text))
    voltage_rating: Optional[str] = Field(default=None, sa_column=Column("voltage_rating_kv", Float(2)))
    village: Optional[str] = Field(default=None, sa_column=Column("village", Text))
    municipality: Optional[str] = Field(default=None, sa_column=Column("municipality", Text))
    image: Optional[str] = Field(default=True , sa_column=Column("image", Text))
    
# NODES
class localNodes(SQLModel, table = True):
    __tablename__:str = "bus"
    metadata = local_metadata
    id:Optional[int] = Field(default=None, sa_column=Column("id", Integer, primary_key=True))
    geom: Optional[str] = Field(default=None, sa_column=Column(name="geom", type_=Geometry("POINT", 4326)))
    bus_id: Optional[str] = Field(default=None, sa_column=Column(name="bus_id", type_=Text))
    pole_id: Optional[str] = Field(default=None, sa_column=Column(name="pole_id", type_=Text))
    description: Optional[str] = Field(default=None, sa_column=Column(name="description", type_=Text))
    nominal_voltage: Optional[float] = Field(default=None, sa_column=Column(name="nominal_voltage_kv", type_=Numeric(10,2)))
    village: Optional[str] = Field(default=None, sa_column=Column(name="village", type_= Text))
    municipality: Optional[str] = Field(default=None, sa_column=Column(name="municipality", type_=Text))
    feeder: Optional[str] = Field(default=None, sa_column=Column(name="feeder", type_=Text))
    image: Optional[str] = Field(default=None, sa_column=Column(name="image", type_=Text))
# primary line
class localPrimaryLine(SQLModel, table = True):
    __tablename__:str = "primary_line"
    metadata = local_metadata
    id:Optional[str] = Field(default=None, sa_column=Column(name="id", type_=Integer, primary_key=True))
    geom: Optional[str] = Field(default=None, sa_column=Column(name="geom", type_=Geometry("LINESTRING", 4326)))
    primary_line_id: Optional[str] = Field(sa_column=Column(default=None,name="primary_line_id", type_=Text))
    from_bus_id: Optional[str] = Field(Column(default=None, name="from_bus_id", type_=Text))
    to_bus_id: Optional[str] = Field(Column(default=None, name="to_bus_id", type_=Text))
    phasing: Optional[str] = Field(Column(name="phasing", default=None, type_=Text))
    description: Optional[str] = Field(Column(name="description", default=None, type_=Text))
    configuration: Optional[str] = Field(Column(name="configuration", default=None, type_=Text))
    assembly: Optional[str] = Field(Column(name="assembly", default= None, type_=Text))
    system_grounding_type: Optional[str] = Field(Column(name="system_grounding_type", default= None, type_=Text))
    length_meters: Optional[str] = Field(Column(name="length_meters", default=None, type_=Numeric(10,4)))
    conductor_type: Optional[str] = Field(Column(name="conductor_type", default=None, type_=Text))
    neutral_wire_type: Optional[str] = Field(Column(name="neutral_wire_type", default=None, type_=Text))
    earth_resistivity: Optional[str] = Field(Column(name="earth_resistivity", default=None, type_=Integer))
    village: Optional[str] = Field(Column(name="village", default=None, type_=Text))
    municipality: Optional[str] = Field(Column(name="municipality", default=None, type_=Text))
    

class localDistributionTransformer(SQLModel, table=True):
    __tablename__:str= "distribution_transformer"
    metadata = local_metadata
    id:Optional[int] = Field(sa_column=Column(name="id", type_=Integer, primary_key=True))
    geom:Optional[str] = Field(sa_column=Column(name="geom", type_=Geometry("POINT", 4326)))
    transformer_id:Optional[str] = Field(sa_column=Column(name='transformer_id', type_=Text))
    from_primary_bus_id:Optional[str] = Field(sa_column=Column(name="from_primary_bus_id", type_=Text))
    to_secondary_bus_id:Optional[str] = Field(sa_column=Column(name="to_secondary_bus_id", type_=Text))
    primary_phasing: Optional[str] = Field(sa_column=Column(name='primary_phasing', type_=Text))
    secondary_phasing: Optional[str] = Field(sa_column=Column(name="secondary_phasing", type_=Text))
    description: Optional[str] = Field(sa_column=Column(name="description", type_=Text))
    installation_type: Optional[str] = Field(sa_column=Column(name="installation_type", type_=Text))
    connection_code: Optional[int] = Field(sa_column=Column(name="connection_code", type_=Integer))
    transformer_type: Optional[str]  = Field(sa_column=Column(name="transformer_type", type_=Text))
    primary_voltage_rating: Optional[float] = Field(sa_column=Column(name="primary_voltage_rating_kv", type_=Numeric(10,2)))
    secondary_voltage_rating: Optional[float] = Field(sa_column=Column(name="secondary_voltage_rating_kv", type_=Numeric(10,2)))
    village: Optional[str] = Field(sa_column=Column(name="village", type_=Text))
    municipality: Optional[str] = Field(sa_column=Column(name="municipality", type_=Text))
    image: Optional[str] = Field(sa_column=Column(name="image", type_=Text))

class localLineBushing(SQLModel, table=True):
    __tablename__:str = "line_bushing"
    metadata=local_metadata
    id:Optional[int] = Field(sa_column=Column(name="id", type_=Integer, primary_key=True))
    geom: Optional[str] = Field(sa_column=Column(name="geom", type_=Geometry("LINESTRING", 4326)))
    line_bushing_id: Optional[str] = Field(sa_column=Column(name="line_bushing_id", type_=Text))
    from_bus_id: Optional[str] = Field(sa_column=Column(name="from_bus_id", type_=Text))
    to_bus_id: Optional[str] = Field(sa_column=Column(name="to_bus_id", type_=Text))
    phasing: Optional[str]  = Field(sa_column=Column(name="phasing", type_=Text))
    description: Optional[str] = Field(sa_column=Column(name="description", type_=Text))
    conductor_type: Optional[str] = Field(sa_column=Column(name="conductor_type", type_=Text))
    length_meters: Optional[float] = Field(sa_column=Column(name="length_meters", type_=Numeric(10, 4)))
    village: Optional[str] = Field(sa_column=Column(name="village" , type_=Text))
    municipality: Optional[str] = Field(sa_column=Column(name="municipality", type_=Text))
    
