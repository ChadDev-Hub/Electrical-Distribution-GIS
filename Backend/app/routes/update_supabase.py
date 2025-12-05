from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import select, Text, cast, func, null, Integer, distinct, and_, distinct
from sqlalchemy.dialects.postgresql import insert
from ..db.sessesion import Db
from sqlmodel.ext.asyncio.session import AsyncSession
from ..db.local_model import localFranchiseArea,localSubstation, localNodes, localPrimaryLine,localDistributionTransformer, localLineBushing
from ..db.supa_model import FranchiseArea, Substation, Nodes, PrimaryLines, DistributionTransformer, TransformerType, LineBushing
from geoalchemy2.shape import to_shape
from geoalchemy2.functions import ST_Intersects
import geojson
import base64
import re
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
        print(len(to_node))
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