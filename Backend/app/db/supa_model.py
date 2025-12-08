from sqlmodel import Field, Text, SQLModel, Integer, Boolean, Column, MetaData, Float, Numeric, ForeignKey, DDL, Table, Relationship, Computed, Index
from sqlalchemy import events, event
from geoalchemy2 import Geometry
from typing import Optional, List


# RE-STRUCTURING AND RE-MODELING GIS DATA BASE FOR ELECTRICAL DISTRIBUTION SYSTEM

# META DATA
supa_meta_data = MetaData(schema="gis")
# -----------------------------------------------------------------------------------------------------------------------------------------
# Franchise Area Model
class FranchiseArea(SQLModel, table=True):
    '''This Cover The Total Franchise Area of Distribution System'''
    __tablename__:str = "franchise_area"
    metadata = supa_meta_data
    id: Optional[int] = Field(default=None, sa_column=Column(name="id",type_=Integer, primary_key=True, index=True))
    geom: Optional[str] = Field(default=None, sa_column=Column(name="geom", type_=Geometry("POLYGON",4326)))
    village: Optional[str] = Field(default=None, sa_column=Column(name="village", type_=Text))
    municipality: Optional[str] = Field(default=None, sa_column=Column(name="municipality", type_=Text))
    powerstatus: Optional[str] = Field(default=None, sa_column=Column(name="powerstatus", type_=Text))
    substation: List["Substation"] = Relationship(back_populates="franchise_area")

# -----------------------------------------------------------------------------------------------------------------------------------------
# SUBSTATION MODEL
class Substation(SQLModel, table=True):
    '''This is Substation Table the Node for Substation'''
    __tablename__:str = "substation"
    metadata = supa_meta_data
    id: Optional[int] = Field(sa_column=Column(name="id", type_=Integer, primary_key=True,default= None))
    franchise_area_id:Optional[int] = Field(sa_column=Column(ForeignKey("gis.franchise_area.id"),name="franchise_area_id",type_=Integer,index=True,default=None))
    geom: Optional[str] = Field(sa_column=Column(name="geom", type_=Geometry("POINT",4326),index=True, default=None))
    generator_name: Optional[str] = Field(default=None, sa_column=Column(name="generator_name", type_=Text, unique=True))
    phasing: Optional[str] = Field(sa_column=Column(name="phasing",type_=Text,default=None))
    description: Optional[str] = Field(sa_column=Column(name="description", type_=Text, default=None))
    voltage_rating: Optional[str] = Field(sa_column=Column(name="voltage_rating", type_=Numeric(10,2),default=None))
    village: Optional[str] = Field(sa_column=Column(name="village",type_=Text,default=None))
    municipality: Optional[str] = Field(sa_column=Column(name="municipality", type_=Text, default=None))
    image: Optional[str] = Field(sa_column=Column(name="image", type_=Text,default=None))
    isactive: Optional[bool] = Field(sa_column=Column(name="isactive", type_=Boolean, default=None))
    franchise_area:Optional[FranchiseArea] = Relationship(back_populates="substation")
    nodes: List["Nodes"] = Relationship(back_populates="substation")
  
    
# FUNCTION TO UPDATE FRANCHISE AREA ID
update_franchise_area_id = DDL(
    """
    CREATE OR REPLACE FUNCTION gis.update_franchise_area_id()
    RETURNS TRIGGER AS $$
    DECLARE franchise_area_id int;
    BEGIN
    SELECT f.id
    INTO franchise_area_id
    FROM gis.franchise_area as f
    WHERE st_intersects(f.geom, new.geom)
    LIMIT 1;
    new.franchise_area_id:= franchise_area_id;
    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
)
    
    
# FUNCTION TO UPDATE VILLLAGE AND MUNCIPALITY 
update_village_municipality = DDL("""
    CREATE OR REPLACE FUNCTION gis.update_vill_mun()
    RETURNS TRIGGER AS $$
    DECLARE village text;
    DECLARE municipality text;
    BEGIN
    SELECT f.village, f.municipality  
    INTO village, municipality 
    FROM gis.franchise_area as f where st_intersects(f.geom, new.geom) LIMIT 1;
    new.village:= village;
    new.municipality:= municipality;
    return new;
    END;
    $$ LANGUAGE plpgsql;"""
)

# TRIGGER FOR FRANCHISE AREA
trigger_update_franchise_area_id = DDL(
    """
    DO $$
    BEGIN
    IF NOT EXISTS(
        SELECT 1 FROM pg_trigger WHERE tgname = 'update_franchise_area_id'
    )THEN
    CREATE TRIGGER update_franchise_area_id
    BEFORE INSERT OR UPDATE on gis.substation
    FOR EACH ROW EXECUTE FUNCTION gis.update_franchise_area_id();
    END IF;
    END $$;
    """
)

#  TIGGER
trigger_village_municipality = DDL(
   """
   DO $$
   BEGIN IF NOT EXISTS(
       SELECT 1 FROM pg_trigger WHERE tgname = 'update_village_mun'
   ) THEN 
    CREATE TRIGGER update_village_mun
    BEFORE INSERT OR UPDATE ON gis.substation
    FOR EACH ROW EXECUTE FUNCTION gis.update_vill_mun();
    END IF;
    END $$"""
)



# CHANGE STATUS OF NODES IF SUBSTATION ISACTIVE OR NOT
is_node_active = DDL(
    '''
    CREATE OR REPLACE FUNCTION gis.node_is_active()
    RETURNS TRIGGER AS $$
    BEGIN
    UPDATE gis.nodes as n
    SET isactive = new.isactive
    WHERE n.substation_id = new.id;

    UPDATE gis.primary_lines as pl
    SET isactive = new.isactive
    where pl.substation_id = new.id;
    
    UPDATE gis.distribution_transformer as dt
    set isactive = new.isactive
    where dt.substation_id = new.id;

    RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    '''
)

# AFTER INSERT AND UPDATE TO THE NODES IT WILL EXECUTE A FUNCTION
node_status_update_trigger = DDL(
    '''
    DO $$
    BEGIN 
    IF NOT EXISTS(
        SELECT 1 FROM pg_trigger WHERE tgname = 'node_is_active'
    ) THEN
    CREATE TRIGGER node_is_active
    AFTER INSERT OR UPDATE ON gis.substation
    FOR EACH ROW EXECUTE FUNCTION gis.node_is_active();
    END IF;
    END $$ 
    '''
)
    
# ----------------------------------------------------------------------------------------------------------------------------------------- 
# ENUM TY
# BUS OR NODE DATA MODEL
class Nodes(SQLModel, table=True):
    '''EXPLICIT NODE FOR CONNECTIONS,FOR SUBSTATION, POLES, AND LINES'''
    __tablename__:str = "nodes"
    metadata = supa_meta_data
    id: Optional[int] = Field(default=None,sa_column=Column(name="id",unique=True,primary_key=True, type_=Integer))
    geom: Optional[str] = Field(default=None, sa_column=Column(name="geom", type_=Geometry("POINT", 4326), index=True))
    substation_id: Optional[int] = Field(default=None, sa_column=Column(ForeignKey("gis.substation.id"), name="substation_id", type_=Integer))
    node_name: Optional[str] = Field(default=None, sa_column=Column(name="node_name", type_=Text, unique=True))
    description: Optional[str] = Field(default=None, sa_column=Column(name="description", type_=Text))
    nominal_voltage_kv: Optional[float] = Field(default=None, sa_column=Column(name="nominal_voltage_kv", type_=Numeric(10,2)))
    village:Optional[str] = Field(default=None, sa_column=Column(name="village", type_=Text))
    municipality:Optional[str] = Field(default=None, sa_column=Column(name="municipality", type_=Text))
    isactive:Optional[bool] = Field(default=None,sa_column=Column(name="isactive",type_=Boolean))
    remarks:Optional[str] = Field(default=None, sa_column=Column(name="remarks", type_=Text))
    substation: Optional[Substation] = Relationship(back_populates="nodes")
    primary_lines: Optional["PrimaryLines"] = Relationship(back_populates="nodes")

# MAIN TRIGGER FUNCTION TRIGGER FOR NODES BEFORE INSERT OR UPDATE

# FUNCTION TO UPDATE SUBSTATION_ID  OF NODES TABLE
nodes_substation_function = DDL(
    """
    CREATE OR REPLACE FUNCTION gis.update_nodes_substation_id()
    RETURNS TRIGGER AS $$
    DECLARE substation_id int;
    BEGIN
        IF EXISTS(
            SELECT 1 FROM gis.substation as sub
            WHERE ST_INTERSECTS(sub.geom, new.geom)
        )THEN
            SELECT s.id
            INTO substation_id
            FROM gis.substation as s
            WHERE ST_INTERSECTS(s.geom, new.geom) AND new.description ilike '%%primary%%'
            LIMIT 1;
        new.substation_id:= substation_id;
        END IF;
    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
)


# TRIGGER FOR UPDATING SUBSTATION_ID OF GIS.NODES
nodes_substation_id_trigger = DDL(
    """
    DO
    $$
    BEGIN
        IF NOT EXISTS(
            SELECT 1 FROM pg_trigger where tgname = 'update_nodes_substation_id'
        ) THEN
        CREATE TRIGGER update_nodes_substation_id
        BEFORE INSERT OR UPDATE ON gis.nodes
        FOR EACH ROW EXECUTE FUNCTION gis.update_nodes_substation_id();
        END IF;
    END $$;
    """
)

# TRIGGER THAT CAST BEFORE INSERT OR UPDATE ON NODES TABLE
nodes_trigger = DDL(
    '''
    DO $$
    BEGIN
    IF NOT EXISTS(
        SELECT 1 FROM pg_trigger where tgname = 'update_nodes'
    ) THEN
    CREATE TRIGGER update_nodes
    BEFORE INSERT OR UPDATE ON gis.nodes
    FOR EACH ROW EXECUTE FUNCTION gis.update_vill_mun();
    END IF;
    END $$;
    '''
)

# -----------------------------------------------------------------------------------------------------------------------------------------
# PRIMARY LINE MODEL
class PrimaryLines(SQLModel, table=True):
    __tablename__:str = "primary_lines"
    metadata = supa_meta_data
    id: Optional[int] = Field(default=None,sa_column=Column(name="id", type_=Integer, primary_key=True))
    node_id: Optional[int] = Field(default=None, sa_column=Column(ForeignKey("nodes.id"), name="node_id", type_=Integer))
    substation_id: Optional[int] = Field(default=None, sa_column=Column(name="substation_id", type_=Integer))
    geom: Optional[str] = Field(default=None, sa_column=Column(name="geom",type_=Geometry("LINESTRING", 4326), index=True))
    line_id: Optional[str] = Field(default=None, sa_column=Column(name="line_id", type_=Text, unique=True))
    from_node: Optional[str] = Field(default=None, sa_column=Column(name="from_node", type_=Text))
    to_node: Optional[str] = Field(default=None, sa_column=Column(name="to_node", type_=Text))
    phasing: Optional[str] = Field(default=None, sa_column=Column(name="phasing", type_=Text))
    description: Optional[str] = Field(default=None, sa_column=Column(name="description", type_=Text))
    configuration: Optional[str] = Field(default=None, sa_column=Column(name="configuration", type_=Text))
    system_grounding_type: Optional[str] = Field(default=None, sa_column=Column(name="system_grounding_type", type_=Text))
    length: Optional[int] = Field(default=None, sa_column=Column(Computed("ST_LENGTH(ST_TRANSFORM(GEOM,3857)) + (ST_LENGTH(ST_TRANSFORM(GEOM,3857)) * 0.10)", persisted=True),name="length_meters", type_=Numeric(10,2)))
    conductor_type: Optional[str] = Field(default=None, sa_column=Column(name="conductor_type", type_=Text))
    neutral_wire_type: Optional[str] = Field(default=None, sa_column=Column(name="neutral_wire_type",type_=Text))
    earth_resistivity: Optional[int] = Field(default=None, sa_column=Column(name="earth_resistivity", type_=Integer))
    village: Optional[str] = Field(default=None, sa_column=Column(name="village", type_=Text))
    isactive: Optional[bool] = Field(default=False, sa_column=Column(name="isactive", type_=Boolean))
    municipality: Optional[str] = Field(default=None, sa_column=Column(name="municipality", type_=Text))
    nodes: Optional[Nodes] = Relationship(back_populates="primary_lines")

# TRIGGER FUNCTION FOR PRIMARY LINE
update_primary_line= DDL(
    """
    CREATE OR REPLACE FUNCTION gis.update_primary_line()
    RETURNS TRIGGER AS $$
    DECLARE node_id int;
    DECLARE substation_id int;
    DECLARE from_node TEXT;
    DECLARE to_node Text;
    DECLARE village text;
    DECLARE municipality text;
    BEGIN
    
    SELECT n.substation_id, n.node_name
    INTO substation_id, from_node
    from gis.nodes as n
    WHERE ST_INTERSECTS(n.geom, ST_STARTPOINT(new.geom))
    AND n.description ILIKE '%%PRIMARY%%'
    LIMIT 1;
    
    SELECT f.village, f.municipality, f.node_name, f.id
    INTO village, municipality, to_node, node_id
    FROM gis.nodes as f
    WHERE ST_INTERSECTS(f.geom , ST_ENDPOINT(new.geom))
    AND f.description ILIKE '%%PRIMARY%%';
    new.node_id:= node_id;
    new.substation_id:= substation_id;
    new.from_node:= from_node;
    new.to_node:= to_node;
    new.village:= village;
    new.municipality:= municipality;
    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
)
# TIGGER BEFORE INSERT OR UPDATE
update_primary_line_trigger = DDL(
    """
    DO
    $$
    BEGIN
        IF NOT EXISTS(
            SELECT 1 FROM pg_trigger WHERE tgname = 'primary_line_update'
        )THEN
        CREATE TRIGGER primary_line_update
        BEFORE INSERT OR UPDATE ON gis.primary_lines
        FOR EACH ROW EXECUTE FUNCTION gis.update_primary_line();
        END IF;
    END $$;
    """
)

update_node_substation_id = DDL(
    """
    CREATE OR REPLACE FUNCTION gis.pl_update_node_substation_id()
    RETURNS TRIGGER AS $$
    BEGIN
        UPDATE gis.nodes as n
        SET substation_id = new.substation_id
        WHERE n.id = NEW.node_id
        AND n.description ILIKE '%%PRIMARY%%';
    RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;
    """
)

update_node_substation_id_trigger = DDL(
    """
    DO
    $$
    BEGIN
        IF NOT EXISTS(
            SELECT 1 FROM pg_trigger WHERE tgname = 'pl_update_nodes_substation'
        )THEN
        CREATE TRIGGER pl_update_nodes_substation
        AFTER INSERT OR UPDATE ON gis.primary_lines
        FOR EACH ROW EXECUTE FUNCTION gis.pl_update_node_substation_id();
        END IF;
    END $$;
    """
)

# -----------------------------------------------------------------------------------------------------------------------------------------
# TRANSFORMER
class DistributionTransformer(SQLModel, table=True):
    __tablename__:str = "distribution_transformer"
    metadata = supa_meta_data
    id: Optional[int] = Field(sa_column=Column(name="id",primary_key=True,type_=Integer))
    geom: Optional[str] = Field(sa_column=Column(name="geom", type_=Geometry("POINT",4326), index=True))
    substation_id: Optional[int] = Field(sa_column=Column(name="substation_id", type_=Integer))
    line_bushing_id: Optional[int] = Field(sa_column=Column(ForeignKey("line_bushing.id"),name="line_bushing_id",type_=Integer))
    transformer_id: Optional[str] = Field(sa_column=Column(name="transformer_id", type_=Text, unique=True))
    from_primary_node: Optional[str] = Field(sa_column=Column(name="from_primary_node", type_=Text))
    to_secondary_node: Optional[str] = Field(sa_column=Column(name="to_secondary_node", type_=Text))
    primary_phasing: Optional[str]  = Field(sa_column=Column(name="primary_phasing", type_=Text))
    secondary_phasing: Optional[str] = Field(sa_column=Column(name="secondary_phasing", type_=Text))
    description: Optional[str] = Field(sa_column=Column(name="description", type_=Text))
    installation_type: Optional[str] = Field(sa_column=Column(name="installation_type", type_=Text))
    connection_code: Optional[int] = Field(sa_column=Column(name="connection_code", type_=Integer))
    transformer_type: Optional[str] = Field(sa_column=Column(ForeignKey("transformer_type.name"),name="transformer_type", type_=Text))
    primary_voltage_rating: Optional[float] = Field(sa_column=Column(name="primary_voltage_rating", type_=Numeric(10,2)))
    secondary_voltage_rating: Optional[float] = Field(sa_column=Column(name="secondary_voltage_rating", type_=Numeric(10,2)))
    village: Optional[str] = Field(sa_column=Column(name="village", type_=Text))
    municipality: Optional[str] = Field(sa_column=Column(name="municipality", type_=Text))
    image: Optional[str] = Field(sa_column=Column(name="image", type_=Text))
    isactive: Optional[bool] = Field(sa_column=Column(name="isactive", type_=Boolean))
    dt_type: Optional["TransformerType"] = Relationship(
        back_populates="distribution_transformer",
        sa_relationship_kwargs=dict(
        primaryjoin = "DistributionTransformer.transformer_type == TransformerType.name",
        foreign_keys="DistributionTransformer.transformer_type"
    ))

dt_switch_function = DDL(
    """
CREATE OR REPLACE FUNCTION gis.dt_switch_function()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE gis.secondary_lines as sl
    set isactive = new.isactive
    WHERE new.transformer_id = sl.dt_id;
RETURN NEW;
END
$$ LANGUAGE plpgsql;
"""
)

dt_switch_trigger = DDL(
    """
DO
$$
BEGIN
IF NOT EXISTS(SELECT 1 FROM pg_trigger where tgname = 'dt_switch_trigg')
THEN 
CREATE trigger dt_switch_trigg
AFTER INSERT OR UPDATE ON gis.distribution_transformer
FOR EACH ROW EXECUTE FUNCTION gis.dt_switch_function();
END IF;
END $$; 
"""
)

# TRANSFORMER TYPE
class TransformerType(SQLModel, table=True):
    __tablename__:str = "transformer_type"
    metadata = supa_meta_data
    id:Optional[int] = Field(sa_column=Column(name="id",primary_key=True, type_=Integer))
    name: Optional[str] = Field(sa_column=Column(name="name", unique=True, type_=Text))
    kva_rating: Optional[float]= Field(sa_column=Column(name="kva_rating", type_=Numeric(10,2)))
    distribution_transformer: List["DistributionTransformer"] = Relationship(back_populates="dt_type")

# Conductor Type
class ConductorType(SQLModel, table=True):
    __tablename__:str = "conductor_type"
    metadata = supa_meta_data
    id: Optional[int] = Field(sa_column=Column(name="id", primary_key=True, type_=Integer))
    name: Optional[str] = Field(sa_column=Column(name="name", unique=True, type_=Text))

# TRANSFORMER LINE BUSHING
class LineBushing(SQLModel, table=True):
    __tablename__:str = "line_bushing"
    metadata = supa_meta_data
    id: Optional[int] = Field(sa_column=Column(name="id", primary_key=True, type_=Integer))
    geom: Optional[str] = Field(sa_column=Column(name="geom", type_=Geometry("LINESTRING", 4326), index=True))
    substation_id: Optional[int] = Field(sa_column=Column(name="substation_id", type_=Integer))
    primary_line_id: Optional[int] = Field(sa_column=Column(ForeignKey("primary_lines.id"),name="primary_line_id", type_=Integer))
    line_bushing_name: Optional[str] = Field(sa_column=Column(name="line_bushing_name", type_=Text, unique=True))
    from_node_id: Optional[str] = Field(sa_column=Column(name="from_node_id", type_=Text))
    to_node_id: Optional[str] = Field(sa_column=Column(name="to_node_id", type_=Text))
    phasing: Optional[str] = Field(sa_column=Column(name="phasing", type_=Text))
    description: Optional[str] = Field(sa_column=Column(name="description", type_=Text))
    conductor_type: Optional[str] = Field(sa_column=Column(ForeignKey("conductor_type.name"),name="conductor_type", type_=Text))
    length_meters: Optional[float] = Field(sa_column=Column(Computed("1.500", persisted=True),name="length_meters", type_=Numeric(10, 4)))
    village: Optional[str] = Field(sa_column=Column(name="village", type_=Text))
    municipality: Optional[str] = Field(sa_column=Column(name="municipality", type_=Text))
    
line_bushing_update = DDL(
    '''
    CREATE OR REPLACE FUNCTION gis.line_bushing_update()
    RETURNS TRIGGER AS 
    $$
    DECLARE substation_id int;
    DECLARE primary_line_id int;
    DECLARE from_node_id text;
    DECLARE description text;
    DECLARE to_node_id text;
    DECLARE village text;
    DECLARE municipality text;
    BEGIN
    if exists(select 1 from gis.primary_lines as pl where st_intersects(st_endpoint(pl.geom), ST_STARTPOINT(new.geom)))
    THEN 
        SELECT 
        pl.substation_id,
        pl.to_node,
        pl.id,  
        'PRIMARY LINE BUSHING',
        pl.village,
        pl.municipality
        INTO
        substation_id,
        from_node_id,
        primary_line_id,
        description,
        village,
        municipality
        from gis.primary_Lines as pl
        where st_intersects(st_endpoint(pl.geom), st_startpoint(new.geom))
        limit 1;
        
        SELECT 
            dt.transformer_id
            into 
            to_node_id
            from gis.distribution_transformer as dt
            where st_intersects(dt.geom, st_endpoint(new.geom))
            limit 1;
    ELSIF EXISTS (SELECT 1 FROM gis.distribution_transformer as dt where st_intersects(dt.geom, st_STARTPOINT(new.geom)))
    THEN 
        SELECT 
        dt.substation_id,
        dt.transformer_id,
        'SECONDARY LINE BUSHING',
        dt.village,
        dt.municipality
        INTO
        substation_id,
        from_node_id,
        description,
        village,
        municipality
        from gis.distribution_transformer as dt
        where st_intersects(dt.geom, st_startpoint(new.geom))
        LIMIT 1;

        select 
        lb.primary_line_id
        into primary_line_id
        from gis.line_bushing as lb
        where st_intersects(st_endpoint(lb.geom), st_startpoint(new.geom))
        limit 1;
        
        select
        n.node_name
        INTO 
        to_node_id
        from gis.nodes as n
        where st_intersects(n.geom, st_endpoint(new.geom))
        LIMIT 1;
    END IF;
    NEW.substation_id:= substation_id;
    NEW.primary_line_id:= primary_line_id;
    NEW.from_node_id:= from_node_id;
    NEW.to_node_id:= to_node_id;
    NEW.description:= description;
    NEW.village:= village;
    NEW.municipality:= municipality;
    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    '''
)

line_bushing_trigger = DDL(
    """
    DO
    $$
    BEGIN
    IF NOT EXISTS(
        SELECT 1 FROM pg_trigger 
        where tgname = 'line_bushing_trigger'
    ) THEN
    CREATE TRIGGER line_bushing_trigger
    Before insert or update on gis.line_bushing
    FOR EACH row execute function gis.line_bushing_update();
    END IF;
    END $$;
    """
)


line_bushing_after_update = DDL(
    """
    CREATE OR REPLACE FUNCTION gis.line_bushing_after_update()
    RETURNS TRIGGER AS 
    $$
    BEGIN 
    if new.description ilike '%%Primary%%' THEN
    UPDATE gis.distribution_transformer as dt
    set 
    substation_id = new.substation_id,
    line_bushing_id = new.id,
    from_primary_node = new.from_node_id,
    primary_phasing = new.phasing,
    village = new.village,
    municipality = new.municipality
    where new.to_node_id =  dt.transformer_id;
    ELSIF new.description ILIKE '%%SECONDARY%%' THEN
    UPDATE gis.distribution_transformer as dt
    set
    to_secondary_node = new.to_node_id,
    secondary_phasing = new.phasing
    where new.from_node_id = dt.transformer_id;
    END IF;
    RETURN NEW;
    END;
    $$ LANGUAGE plpgsql; 
    """
)

line_bushing_after_trigger  = DDL(
    """
    DO
        $$
        BEGIN
        IF NOT EXISTS (
            SELECT 1 from pg_trigger
            where tgname = 'line_bushing_update_after'
        ) THEN
        CREATE TRIGGER  line_bushing_update_after
        AFTER INSERT OR UPDATE on gis.line_bushing
        FOR EACH ROW EXECUTE FUNCTION gis.line_bushing_after_update();
        END IF;
    END $$;
    """
)

# SECONDARY LINE
class SecondarLines(SQLModel, table = True):
    __tablename__:str = "secondary_lines"
    metadata = supa_meta_data
    __table_args__ = (Index("secondary_lines_geom_gix", "geom", postgresql_using="gist"),)
    id: Optional[str] = Field(sa_column=Column(name="id", type_=Integer, primary_key=True))
    line_bushing_id: Optional[int] = Field(sa_column=Column(ForeignKey("line_bushing.id"), type_=Integer))
    dt_id: Optional[str] = Field(sa_column=Column(name="dt_id", type_=Text))
    geom: Optional[str] = Field(sa_column=Column(name="geom", type_=Geometry("LINESTRING", 4326)))
    secondary_line_id: Optional[str] = Field(sa_column=Column(name="secondary_line_id", type_=Text, unique=True))
    from_node: Optional[str] = Field(sa_column=Column(name="from_node", type_=Text))
    to_node: Optional[str] = Field(sa_column=Column(name="to_node", type_=Text))
    phasing: Optional[str] = Field(sa_column=Column(name="phasing", type_=Text))
    description: Optional[str] = Field(sa_column=Column(name="description", type_=Text))
    length_meters: Optional[float] = Field(sa_column=Column(Computed("case when ST_LENGTH(ST_TRANSFORM(GEOM,3857)) < 5 then 5 else ST_LENGTH(ST_TRANSFORM(GEOM,3857)) + (ST_LENGTH(ST_TRANSFORM(GEOM,3857)) * 0.10) END "),name="length_meter", type_=Numeric(10,2)))
    conductor_type: Optional[str] = Field(sa_column=Column(name="conductor_type", type_=Text))
    village: Optional[str] = Field(sa_column=Column(name="village", type_=Text))
    municipality: Optional[str] = Field(sa_column=Column(name="municipality", type_=Text))
    isactive: Optional[bool] = Field(sa_column=Column(name="isactive", type_=Boolean))


secondary_line_update = DDL(
    '''CREATE OR REPLACE FUNCTION gis.secondary_line_update()
    RETURNS TRIGGER AS $$
    DECLARE line_bushing_id int;
    DECLARE dt_id text;
    DECLARE from_node text;
    DECLARE to_node text;
    DECLARE phasing text;
    DECLARE village text;
    DECLARE municipality text;
    BEGIN
        if exists(
        select 1 from gis.nodes as n
        inner join gis.line_bushing as lb
        on lb.to_node_id = n.node_name
        where st_intersects(n.geom, st_Startpoint(new.geom))
        and n.description ilike '%%SECONDARY%%')
        then
        select lb.id, lb.from_node_id, lb.to_node_id, lb.phasing, lb.village, lb.municipality
        into line_bushing_id, dt_id, from_node, phasing, village, municipality
        from gis.nodes as n
        inner join gis.line_bushing as lb
        on lb.to_node_id = n.node_name
        where
        st_intersects(n.geom, st_startpoint(new.geom))
        and n.description ILIKE '%%SECONDARY%%'
        LIMIT 1;

        elsif exists(select 1 from gis.nodes as n
        inner join gis.secondary_lines as sl
        on sl.to_node = n.node_name
        where st_intersects(n.geom, st_startpoint(new.geom)))
        then
        select sl.line_bushing_id, sl.dt_id, sl.to_node, sl.phasing, sl.village, sl.municipality
        into
        line_bushing_id, dt_id, from_node, phasing, village, municipality
        from gis.nodes as n
        inner join gis.secondary_lines as sl
        on sl.to_node = n.node_name
        where st_intersects(n.geom, st_startpoint(new.geom))
        and n.description ilike '%%SECONDARY%%'
        LIMIT 1;
        END IF
        ;

        select n.node_name
        into to_node
        from gis.nodes as n where st_intersects(n.geom, st_endpoint(new.geom))
        and n.description ilike '%%SECONDARY%%'
        LIMIT 1;

        NEW.line_bushing_id:= line_bushing_id;
        NEW.dt_id:= dt_id;
        NEW.from_node:= from_node;
        NEW.to_node:= to_node;
        NEW.phasing:= phasing;
        NEW.village:= village;
        NEW.municipality:= municipality;
        
        RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    ''')

secondary_line_update_trigger = DDL(
    '''
    DO
    $$
    BEGIN
        if not exists(select 1 from pg_trigger 
        where tgname= 'secondary_line_update_trigger')
        THEN 
        CREATE trigger secondary_line_update_trigger
        BEFORE INSERT OR UPDATE on gis.secondary_lines
        FOR EACH ROW execute function gis.secondary_line_update();
        END IF;
    END $$;
    '''
)

sl_after_function = DDL(
    """
    CREATE OR REPLACE FUNCTION gis.sl_after_func()
    RETURNS TRIGGER AS $$
    BEGIN
    UPDATE gis.service_drop as sd 
    set isactive = new.isactive
    where sd.secondary_line_id = new.id;
    RETURN NEW;
    END;
    $$ LANGUAGE PLPGSQL;
    """
)

sl_after_trigg = DDL(
    """
    DO
        $$
        BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_trigger where tgname = 'sl_after_trigg')
        THEN
        CREATE trigger sl_after_trigg
        AFTER INSERT OR UPDATE ON gis.secondary_lines
        FOR EACH ROW EXECUTE FUNCTION gis.sl_after_func();
        END IF;
    END $$;
    """
)

# SERVICE DROP
class ServiceDrop(SQLModel, table = True):
    __tablename__:str = "service_drop"
    metadata = supa_meta_data
    id: Optional[int] = Field(sa_column=Column(name="id", type_=Integer, primary_key=True))
    dt_id: Optional[str]  = Field(sa_column=Column(name="dt_id", type_=Text))
    secondary_line_id:Optional[int] = Field(sa_column=Column(ForeignKey("secondary_lines.id"),name="secondary_line_id", type_=Integer, nullable=True))
    geom: Optional[str] = Field(sa_column=Column(name="geom", type_=Geometry("LINESTRING", 4326)))
    service_drop_id: Optional[str] = Field(sa_column=Column(name="service_drop_id", type_=Text, unique=True))
    from_node: Optional[str] = Field(sa_column=Column(name="from_node", type_=Text))
    to_customer: Optional[str] = Field(sa_column=Column(name="to_customer", type_=Text))
    phasing:Optional[str] = Field(sa_column=Column(name="phasing", type_=Text))
    descripiton:Optional[str] = Field(sa_column=Column(name="description", type_=Text))
    length_meter1: Optional[float] = Field(sa_column=Column(Computed("30", persisted=True),name="length_meter1", type_=Numeric(10,2)))
    length_meter2: Optional[float] = Field(sa_column=Column(Computed("st_length(st_transform(geom, 3857))"),name="length_meter2", type_=Numeric(10,2)))
    conductor_type: Optional[str] = Field(sa_column=Column(name="conductor_type", type_=Text))
    village: Optional[str] = Field(sa_column=Column(name="village", type_=Text))
    municipality: Optional[str] = Field(sa_column=Column(name="municipality", type_=Text))
    isactive: Optional[bool] = Field(sa_column=Column(name="isactive" , type_=Boolean))


sd_update_function = DDL(
    """
    CREATE OR REPLACE FUNCTION gis.servicedrop_function()
    RETURNS TRIGGER AS $$
    DECLARE secondary_line_id int;
    DECLARE dt_id text;
    DECLARE from_node text;
    DECLARE to_customer text;
    DECLARE phasing text;
    DECLARE village text;
    DECLARE municipality text;
    BEGIN
        if exists(select 1 from gis.nodes as n
        inner join gis.secondary_lines as sl
        on sl.to_node = n.node_name
        where st_intersects(n.geom, st_startpoint(new.geom))
        and
        n.description ILIKE '%%SECONDARY%%')
        THEN 
            SELECT sl.id, sl.dt_id, sl.to_node, sl.phasing, sl.village, sl.municipality
            INTO secondary_line_id, dt_id, from_node, phasing, village , municipality
            FROM gis.nodes as n
            inner join gis.secondary_lines as sl
            on sl.to_node = n.node_name
            where st_intersects(n.geom, st_startpoint(new.geom))
            AND NEW.description ILIKE '%%SECONDARY%%'
            LIMIT 1;

        elsif exists(SELECT 1 FROM gis.nodes as n
        inner join gis.line_bushing as lb
        on lb.to_node_id = n.node_name
        where st_intersects(n.geom, st_startpoint(new.geom))
        AND n.description ILIKE '%%SECONDARY%%')
            THEN
            select lb.from_node_id, lb.to_node_id, lb.phasing, lb.village, lb.municipality
            INTO dt_id, from_node, phasing, village, municipality
            FROM gis.nodes as n
            inner join gis.line_bushing as lb
            on lb.to_node_id = n.node_name 
            where st_intersects(n.geom, st_startpoint(new.geom))
            AND new.description ilike '%%SECONDARY%%'
            LIMIT 1;
        ELSIF EXISTS(SELECT 1 FROM gis.nodes as n
        INNER JOIN gis.line_bushing as lb
        on lb.from_node_id = n.node_name
        WHERE ST_INTERSECTS(n.geom, new.geom)
        AND n.description ilike '%%PRIMARY%%')
        THEN
            SELECT lb.to_node_id, lb.from_node_id,lb.phasing, lb.village, lb.municipality
            INTO dt_id, from_node, phasing, village, municipality
            FROM gis.nodes as n
            INNER JOIN gis.line_bushing as lb
            ON LB.from_node_id = n.node_name
            where st_intersects(n.geom, st_startpoint(new.geom))
            AND new.description ILIKE '%%PRIMARY%%';
        END IF;

        SELECT 
        c.consumer_id
        INTO to_customer 
        from gis.consumer as c
        where st_intersects(c.geom, st_endpoint(new.geom));

        NEW.secondary_line_id:= secondary_line_id;
        NEW.dt_id:= dt_id;
        NEW.from_node:= from_node;
        NEW.To_customer:= to_customer;
        NEW.phasing:= phasing;
        NEW.village:= village;
        NEW.municipality:= municipality;
        
        RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
)

sd_update_trigger = DDL(
    """
    DO
    $$
    BEGIN
        IF NOT EXISTS(SELECT 1 FROM pg_trigger
        WHERE tgname = 'sd_update_trigger')
        then 
        CREATE trigger sd_update_trigger
        BEFORE INSERT OR UPDATE on gis.service_drop
        FOR EACH ROW execute function gis.servicedrop_function();
        END IF;
    END $$;
    """
)

sd_after_function = DDL(
    """
CREATE OR REPLACE function gis.sd_after_update_func()
RETURNS TRIGGER AS $$
BEGIN
UPDATE gis.consumer as c
set
servicedrop_id = NEW.id,
phase = case when length(new.phasing) = 2 THEN 1 when length(new.phasing) = 3 then 2 else 3 end ,
dt_id = NEW.dt_id,
village = NEW.village,
municipality = NEW.municipality,
isactive = NEW.isactive
WHERE c.consumer_id = NEW.to_customer;

RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""
)

sd_after_trigger = DDL(
    """
    DO
    $$
    BEGIN
        IF NOT EXISTS(SELECT 1 FROM pg_trigger where tgname = 'sd_after_trigg')
        THEN
        CREATE trigger sd_after_trigg
        AFTER INSERT OR UPDATE on gis.service_drop
        FOR EACH ROW execute function gis.sd_after_update_func();
    END IF;
    END $$;
"""
)

class Consumer(SQLModel, table = True):
    __tablename__:str = "consumer"
    metadata = supa_meta_data
    id: Optional[int] = Field(sa_column=Column(name="id", type_=Integer, primary_key=True))
    dt_id: Optional[str] = Field(sa_column=Column(name="dt_id", type_=Text))
    service_drop_id: Optional[int] = Field(sa_column=Column(ForeignKey("service_drop.id"),name="servicedrop_id", type_=Integer))
    geom: Optional[str] = Field(sa_column=Column(name="geom", type_=Geometry("POINT", 4326)))
    consumer_id: Optional[str] = Field(sa_column=Column(name="consumer_id", type_=Text, unique=True))
    consumer_name: Optional[str] = Field(sa_column=Column(name="consumer_name", type_=Text))
    consumer_type: Optional[str] = Field(sa_column=Column(name="consumer_type", type_=Text))
    service_voltage: Optional[int] = Field(sa_column=Column(name="service_voltage", type_=Integer))
    description: Optional[str] = Field(sa_column=Column(name="description", type_=Text))
    phase: Optional[str] = Field(sa_column=Column(name="phase", type_=Text))
    meter_brand: Optional[str] = Field(sa_column=Column(name="meter_brand", type_=Text))
    meter_number: Optional[str] = Field(sa_column=Column(name="meter_number", type_=Text))
    village: Optional[str] = Field(sa_column=Column(name="village", type_=Text))
    municipality: Optional[str] = Field(sa_column=Column(name="municipality", type_=Text))
    image: Optional[str] = Field(sa_column=Column(name="image", type_=Text))
    isactive: Optional[bool] = Field(sa_column=Column(name="isactive", type_=Boolean))