from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import select, Text, cast, func, null, Integer, distinct, and_, distinct
from sqlalchemy.dialects.postgresql import insert
from ..db.sessesion import Db
from sqlmodel.ext.asyncio.session import AsyncSession
from ..db.local_model import localFranchiseArea,localSubstation, localNodes, localPrimaryLine,localDistributionTransformer, localLineBushing, localSecondary, LocalConsumer, LocalServiceDrop
from ..db.supa_model import FranchiseArea, Substation, Nodes, PrimaryLines, DistributionTransformer, TransformerType, LineBushing, SecondarLines, Consumer, ServiceDrop
from geoalchemy2.shape import to_shape
from geoalchemy2.functions import ST_Intersects, ST_AsGeoJSON
from json import loads, dumps
from geoalchemy2.elements import WKBElement
from shapely import wkb
import geojson
import base64
import re
import traceback
from ..fileuploader.gd_uploader import SupaFileUploader, GoogleFileUploader
router = APIRouter()

# SUPA ENGINE SESSION
async def get_supa_session():
    async with AsyncSession(Db().supa_engine) as supa_session:
        yield supa_session

# LOCAL ENGINE SESSION
async def get_local_session():
    async with AsyncSession(Db().local_engine) as session:
        yield session

supa_session_dep = Depends(get_supa_session)
local_session_dep = Depends(get_local_session)
file_uploader_dep = Depends(SupaFileUploader)
google_file_uploader = Depends(GoogleFileUploader)


@router.put("/insert/franchise_area")
async def insert_franchise_area(localsession:AsyncSession = local_session_dep, supasession:AsyncSession = supa_session_dep):
    stmt = select(localFranchiseArea)
    data = await localsession.scalars(stmt)
    new_franchise_area = [FranchiseArea(geom=i.geom, village=i.village, municipality=i.municipality, powerstatus=i.status) for i in data]
    supasession.add_all(new_franchise_area)
    await supasession.commit()
    return JSONResponse({"UPSERT STATUS": "Successful"})

@router.put("/upsert/substation")
async def upsert_substation(localsession:AsyncSession = local_session_dep,
                            supasession:AsyncSession = supa_session_dep,
                            fileupload:SupaFileUploader = file_uploader_dep):
    select_stmt = select(localSubstation)
    data  = await localsession.scalars(select_stmt)
    for i in data:
        with open(i.image, "rb") as fs:
            uploadimage = fileupload.uploadFile(filename=i.generator_id, file=fs)
    
        publicl_url = fileupload.getPublicUlr(i.generator_id)
        val = {
            "geom": i.geom,
            "generator_name": i.generator_id,
            "phasing": i.phasing,
            "description": i.description,
            "voltage_rating": i.voltage_rating,
            "village": i.village,
            "municipality": i.municipality,
            "image": publicl_url,
            "isactive": True,
        }
        upsert_stmt = insert(Substation).values(val).on_conflict_do_update(index_elements=["generator_name"], set_={
            "geom": i.geom,
            "phasing": i.phasing,
            "description": i.description,
            "voltage_rating": i.voltage_rating,
            "village": i.village,
            "municipality": i.municipality,
            "image": publicl_url,
            "isactive": True,
        })
        await supasession.exec(upsert_stmt)
    await supasession.commit()
    return JSONResponse({"UPSERT STATUS": "Successful"})

@router.put("/upsert/Node")
async def upsert_nodes(localsession:AsyncSession = local_session_dep, supasession:AsyncSession = supa_session_dep):
    stmt = select(localNodes)
    data = await localsession.scalars(stmt)
    for i in data.fetchall():
        values = {
            "geom": i.geom,
            "node_name": i.bus_id,
            "description": i.description,
            "nominal_voltage_kv": i.nominal_voltage,
            "isactive": True,
            "remarks": None}
        try:
            insert_stmt = insert(Nodes).values(values)
            upsert_stmt = insert_stmt.on_conflict_do_update(index_elements=["node_name"], 
                                                            set_={
                                                                "geom": insert_stmt.excluded.geom,
                                                                "description": insert_stmt.excluded.description,
                                                                "nominal_voltage_kv": insert_stmt.excluded.nominal_voltage_kv,
                                                                "isactive": insert_stmt.excluded.isactive,
                                                                "remarks": insert_stmt.excluded.remarks})
        except Exception:
            print(Exception)                                                                               
        await supasession.exec(upsert_stmt)
    await supasession.commit()
    return JSONResponse(dict(STATUS = "UPSERT SUCCESFULL"))

@router.put("/upsert/primary_lines")
async def upsert_primary_lines(localsession:AsyncSession = local_session_dep, supasession:AsyncSession = supa_session_dep):
    get_villages = await localsession.exec(select(distinct(localPrimaryLine.village)))
    list_of_villages = get_villages.fetchall()

    # PARTIALLY INSERT TO AVOID OVER LAPPING OF PARAMETERS
    for vill in list_of_villages:
        local_stmt = select(localPrimaryLine).where(cast(localPrimaryLine.village, Text) == vill)
        data = await localsession.scalars(local_stmt)
        values = [{"geom": val.geom,
                "line_id": val.primary_line_id,
                "phasing": val.phasing,
                "description": val.description,
                "configuration": val.configuration,
                "system_grounding_type": val.system_grounding_type,
                "conductor_type": val.conductor_type,
                "neutral_wire_type": val.neutral_wire_type,
                "earth_resistivity": int(val.earth_resistivity),
                "isactive": True
                
                }
                for val in data.fetchall()]

        insert_stmt = insert(PrimaryLines).values(values)

        upsert = insert_stmt.on_conflict_do_update(
            index_elements=["line_id"],
            set_={
                "geom": insert_stmt.excluded.geom,
                "phasing": insert_stmt.excluded.phasing,
                "description": insert_stmt.excluded.description,
                "configuration": insert_stmt.excluded.configuration,
                "system_grounding_type": insert_stmt.excluded.system_grounding_type,
                "conductor_type": insert_stmt.excluded.conductor_type,
                "neutral_wire_type": insert_stmt.excluded.neutral_wire_type,
                "earth_resistivity": insert_stmt.excluded.earth_resistivity,
                "isactive": True
            }
        )
        await supasession.exec(upsert)
    await supasession.commit()


@router.put("/update/primary_lines")
async def update_primary_lines(localsession:AsyncSession = local_session_dep, supasession:AsyncSession = supa_session_dep):
    while True:
        select_primary_line_with_substation_id = await supasession.exec(select(PrimaryLines.to_node).where(PrimaryLines.substation_id != None))
        to_node = select_primary_line_with_substation_id.fetchall()

        select_primarY_line_without_substation_id = await supasession.exec(select(PrimaryLines).where(and_(PrimaryLines.from_node.in_(to_node),PrimaryLines.substation_id == None)))
        primary_line_data = select_primarY_line_without_substation_id.fetchall()
        if not primary_line_data:
            break
        values = [
            {
                "geom": val.geom,
                "line_id": val.line_id,
                "phasing": val.phasing,
                "description": val.description,
                "configuration": val.configuration,
                "system_grounding_type": val.system_grounding_type,
                "conductor_type": val.conductor_type,
                "neutral_wire_type": val.neutral_wire_type,
                "earth_resistivity": val.earth_resistivity
            } for val in primary_line_data
        ]

        # UPSERT STATEMENT
        insert_stmt = insert(PrimaryLines).values(values)
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=["line_id"],
            set_={
                "geom": insert_stmt.excluded.geom,
                    "phasing": insert_stmt.excluded.phasing,
                    "description": insert_stmt.excluded.description,
                    "configuration": insert_stmt.excluded.configuration,
                    "system_grounding_type": insert_stmt.excluded.system_grounding_type,
                    "conductor_type": insert_stmt.excluded.conductor_type,
                    "neutral_wire_type": insert_stmt.excluded.neutral_wire_type,
                    "earth_resistivity": insert_stmt.excluded.earth_resistivity
            },
            where=(PrimaryLines.line_id != None)
        )
        await supasession.exec(upsert_stmt)
        await supasession.commit()

@router.put("/upsert/tranformer_type")
async def upsert_transformer_type(supasession:AsyncSession = supa_session_dep, localsession:AsyncSession= local_session_dep):
    dt_transfomer_type_stmt = await localsession.exec(select(distinct(DistributionTransformer.transformer_type)).where(DistributionTransformer.transformer_type != None))
    values = [{"name": val,
               "kva_rating": float(re.findall(r'\d+\.?\d*',val.split(" ")[-1])[0]) if val is not None else None
               } for val in dt_transfomer_type_stmt.fetchall()]
    inset_stmt = insert(TransformerType).values(values)
    upsert_stmt = inset_stmt.on_conflict_do_update(
        index_elements=["name"],
        set_={
            "kva_rating": inset_stmt.excluded.kva_rating
        }
    )
    await supasession.exec(upsert_stmt)
    await supasession.commit()
    
@router.put("/upsert/distribution_tranformer")
async def upsert_dt(supasession:AsyncSession = supa_session_dep, localsession:AsyncSession= local_session_dep, uploader:GoogleFileUploader = google_file_uploader):
    old_dt_stmt = await localsession.exec(select(localDistributionTransformer))
    local_dt_data = old_dt_stmt.fetchall()
    for val in local_dt_data:
        if val.image:
            uploaded_image = uploader.uploadFile(filepath=val.image)
        else:
            uploaded_image = None
        
            
        values = {"geom": val.geom,
                "transformer_id" : val.transformer_id,
                "description" : val.description,
                "installation_type" : val.installation_type,
                "connection_code": val.connection_code,
                "transformer_type" : val.transformer_type,
                "primary_voltage_rating": val.primary_voltage_rating,
                "secondary_voltage_rating" : val.secondary_voltage_rating,
                "image" : uploaded_image}

        insert_stmt = insert(DistributionTransformer).values(values)
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=["transformer_id"],
            set_={
                "description": insert_stmt.excluded.description,
                "installation_type": insert_stmt.excluded.installation_type,
                "connection_code": insert_stmt.excluded.connection_code,
                "transformer_type": insert_stmt.excluded.transformer_type,
                "primary_voltage_rating": insert_stmt.excluded.primary_voltage_rating,
                "secondary_voltage_rating": insert_stmt.excluded.secondary_voltage_rating,
                "image": uploaded_image
            })
        await supasession.exec(upsert_stmt)
        await supasession.commit()
        print(f"UPSERT COMPLETE: {val.transformer_id}")
            

        
    return JSONResponse({
        "UPSERT STATUS": "SUCESSFUL"
    })
    
@router.put("/upsert/line_bushing")
async def upsert_line_bushing(localsession:AsyncSession = local_session_dep, supasession:AsyncSession = supa_session_dep):
    local_bushing = await localsession.exec(select(localLineBushing).where(cast(localLineBushing.description, Text).ilike('%PRIMARY%')))
    
    primary_line_bushing_values = [
        dict(
            geom = val.geom,
            line_bushing_name = val.line_bushing_id,
            phasing = val.phasing     
        ) for val in local_bushing.fetchall()
    ]

    insert_stmt = insert(LineBushing).values(primary_line_bushing_values)
    upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=["line_bushing_name"],
        set_=dict(
            geom = insert_stmt.excluded.geom,
            phasing = insert_stmt.excluded.phasing
        )
    )
    await supasession.exec(upsert_stmt)
    await supasession.commit()
    
    # SECONDARY LINE BUSHING
    local_secondary_line_bushing = await localsession.exec(select(localLineBushing).where(cast(localLineBushing.description, Text).ilike("%SECONDARY%")))
    secondary_line_bushing_val = [
        dict(
            geom = val.geom,
            line_bushing_name = val.line_bushing_id,
            phasing = val.phasing
            ) for val in local_secondary_line_bushing
    ]
    insert_secondary_lb = insert(LineBushing).values(secondary_line_bushing_val)
    upsert_secondary_lb = insert_secondary_lb.on_conflict_do_update(
        index_elements=["line_bushing_name"],
        set_=dict(
            geom = insert_stmt.excluded.geom,
            phasing = insert_stmt.excluded.phasing
        ))
    await supasession.exec(upsert_secondary_lb)
    await supasession.commit()
    return JSONResponse({
        "UPSERT STATUS": "SUCESSFUL"
    })

# ROUTE FOR UPSERTING SECONDARY LINES
@router.put("/upsert/secondary_line")
async def update_secondary_lines(localsession:AsyncSession = local_session_dep, supasession:AsyncSession = supa_session_dep):
    local_secondary_lines = await localsession.exec(select(localSecondary))
    local_sl_data = [dict(
        geom = val.geom,
        secondary_line_id  = val.secondary_line_id,
        description = val.description,
        conductor_type = val.conductor_type,
        isactive = True
    ) for val in local_secondary_lines.fetchall()]
    batch = 1000
    for b in range(0,len(local_sl_data), batch):
        local_sl_value = local_sl_data[b:b+batch]
        insert_stmt = insert(SecondarLines).values(local_sl_value)
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=["secondary_line_id"],
            set_=dict(
                geom = insert_stmt.excluded.geom,
                description = insert_stmt.excluded.description,
                conductor_type = insert_stmt.excluded.conductor_type,
                isactive = insert_stmt.excluded.isactive
            )
        )
        
        await supasession.exec(upsert_stmt)
        await supasession.commit()
        print(f"INSERT SUCCESSFUL: {b}")

    while True:
        connected_sl = await supasession.exec(select(SecondarLines.to_node).where(SecondarLines.dt_id != None))
        connected_sl_data = connected_sl.fetchall()
        print(len(connected_sl_data))
        disconnected_sl = await supasession.exec(select(SecondarLines).where(and_(cast(SecondarLines.from_node, Text).in_(connected_sl_data), SecondarLines.dt_id == None)))
        disconnected_sl_data = disconnected_sl.fetchall()
        print([val.secondary_line_id for val in disconnected_sl_data])
        print(len([val for val in disconnected_sl_data]))
        if not disconnected_sl_data:
            break
        values = [
            dict(
                geom=val.geom,
                secondary_line_id  = val.secondary_line_id,
                description = val.description,
                conductor_type = val.conductor_type,
                isactive = True
                 ) for val in disconnected_sl_data
        ]
        insert_stmt_sl = insert(SecondarLines).values(values)
        upsert_stmt_sl = insert_stmt_sl.on_conflict_do_update(
            index_elements=["secondary_line_id"],
            set_=dict(
                geom = insert_stmt_sl.excluded.geom,
                description = insert_stmt_sl.excluded.description,
                conductor_type = insert_stmt_sl.excluded.conductor_type,
                isactive = insert_stmt_sl.excluded.isactive
            )
        )
        try:
            await supasession.exec(upsert_stmt_sl)
            await supasession.commit()
        except Exception:
            await supasession.rollback()

# ROUTE FOR UPSERTING SERVICE CONSUMER
@router.put("/upsert/consumer")
async def upsert_consumer(localsession:AsyncSession = local_session_dep, supasession:AsyncSession= supa_session_dep):
    local_stmt = await localsession.exec(select(LocalConsumer))
    local_consumer_values = [
        dict(
            geom =val.geom,
            consumer_id = val.customer_id,
            consumer_name = val.customer_name,
            consumer_type = val.customer_type,
            service_voltage = val.service_voltage,
            description = val.description,
            meter_brand = val.brand,
            meter_number = val.meter_number,
            image = val.image
        )
        
         for val in 
        local_stmt.all()]
    
    insert_limit = 500
    for item in range(0,len(local_consumer_values), insert_limit):
        insert_stmt = insert(Consumer).values(local_consumer_values[item:item + insert_limit])
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=["consumer_id"],
            set_=dict(
                geom = insert_stmt.excluded.geom,
                consumer_name = insert_stmt.excluded.consumer_name, 
                consumer_type = insert_stmt.excluded.consumer_type,
                service_voltage = insert_stmt.excluded.service_voltage,
                description = insert_stmt.excluded.description,
                meter_brand = insert_stmt.excluded.meter_brand,
                meter_number = insert_stmt.excluded.meter_number,
                image = insert_stmt.excluded.image
            )
        )
        await supasession.exec(upsert_stmt)
        await supasession.commit()
        print(f"Succesfully upserted {item} :{item + insert_limit} features")
    return JSONResponse({
        "UPSERT" : "SUCCESSFULL"
    })

@router.put("/upsert/service_drop")
async def upsert_service_drop(localsession:AsyncSession = local_session_dep, supasession:AsyncSession= supa_session_dep):
    local_sd_stmt = await localsession.exec(select(LocalServiceDrop))
    local_service_drop_value = [
        dict(
            geom = val.geom,
            service_drop_id = val.service_drop_id,
            description = val.description,
            conductor_type = val.conductor_type,
            isactive = True
        ) for val in local_sd_stmt.all()
    ]
    insert_limit = 500
    for item in range(0, len(local_service_drop_value), insert_limit):
        insert_stmt = insert(ServiceDrop).values(local_service_drop_value[item:item + insert_limit])
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=["service_drop_id"],
            set_=dict(
                geom = insert_stmt.excluded.geom,
                description = insert_stmt.excluded.description,
                conductor_type = insert_stmt.excluded.conductor_type,
                isactive = insert_stmt.excluded.isactive
            )
        )
        await supasession.exec(upsert_stmt)
        await supasession.commit()
        print(f"{item}:{item +insert_limit} Sucessfull Upserted")