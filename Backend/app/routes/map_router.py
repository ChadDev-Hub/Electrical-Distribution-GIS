from fastapi import APIRouter, Depends, WebSocket, Form, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, asc
from ..db.sessesion import Db
from ..db.supa_model import PrimaryLines, Substation, DistributionTransformer, SecondarLines, Consumer
from geoalchemy2 import functions
from geojson import Point, FeatureCollection, Feature, loads, load
from ..sockets.ws import manager
import asyncio
from .dashboard_router import get_inactive_consumer
import os
from dotenv import load_dotenv
import jwt
from jwt.exceptions import PyJWTError
import time

load_dotenv()

map_router = APIRouter()

ORIGIN = os.getenv("ORIGIN")
    

# ASYNC FUNCTION TO YIEL SESSION
async def get_suppasession():
    async with AsyncSession(Db().supa_engine) as session:
        yield session

supasessionDep = Depends(get_suppasession)

# WEB SOCKET MANAGER
# manager = ConnectionManager()

async def get_mapdata(supassession:AsyncSession):
    # SUBSTATION DATA
    substation_data = await supassession.exec(
        select(
            Substation.id,
            functions.ST_AsGeoJSON(Substation.geom).label("geometry"),
            Substation.generator_name,
            Substation.description,
            Substation.voltage_rating,
            Substation.isactive,
            Substation.village,
            Substation.municipality,
            Substation.image
        ).order_by(asc(Substation.id))
    )
    
    sub_feat = {
        "substation": [
            Feature(
                id= substation_id,
                geometry= loads (geometry),
                properties=dict(
                    substation_name = generator_name,
                    description = description,
                    voltage_rating = float(voltage_rating) if voltage_rating is not None else 13.2,
                    isactive = isactive,
                    village = village,
                    municipality = municipality,
                    image = image
                )
            ) for 
            substation_id, 
            geometry, 
            generator_name,
            description,
            voltage_rating, 
            isactive,
            village, 
            municipality,
            image
            in substation_data
        ]
    }
  
    # PRIMARY LINE DATA
    primary_line_data = await supassession.exec(
        select(
            PrimaryLines.id,
            functions.ST_AsGeoJSON(PrimaryLines.geom).label("geometry"),
            PrimaryLines.line_id,
            PrimaryLines.from_node,
            PrimaryLines.to_node,
            PrimaryLines.isactive
            ).order_by(asc(PrimaryLines.id)))
    
    pl_feat = {"primary_lines":[
        Feature(
            id = pl_id,
            geometry = loads(geometry),
            properties = dict(
                primary_line_id = line_id,
                from_node = from_node,
                to_node = to_node,
                isactive = isactive
            )) for pl_id, geometry,line_id, from_node, to_node, isactive in primary_line_data]}
    
    # TRANSFORMER DATA
    transformer_data = await supassession.exec(select(DistributionTransformer.id,
                                                      functions.ST_AsGeoJSON(DistributionTransformer.geom).label("geometry"),
                                                      DistributionTransformer.transformer_id,
                                                      DistributionTransformer.description,
                                                      DistributionTransformer.transformer_type,
                                                      DistributionTransformer.village,
                                                      DistributionTransformer.municipality,
                                                      DistributionTransformer.image,
                                                      DistributionTransformer.isactive
                                                      ).order_by(asc(DistributionTransformer.id)))
    transformer_feat = {
        "distribtion_transformer":
        [
          Feature(
              geometry=loads(dt_geom),
              id= dt_id,
              properties=dict(
                  transformer_id = dt_name,
                  description = dt_descripiton,
                  type = dt_transformer_type,
                  village = dt_village,
                  municipality = dt_municipality,
                  image = dt_image,
                  isactive = dt_isactive
              )
              ) for 
              dt_id,
              dt_geom, 
              dt_name, 
              dt_descripiton,
              dt_transformer_type, 
              dt_village, 
              dt_municipality, 
              dt_image, 
              dt_isactive in transformer_data
        ]
    }
    # SECONDARY LINE DATA
    secondary_line_data = await supassession.exec(select(
        SecondarLines.id,
        functions.ST_AsGeoJSON(SecondarLines.geom).label("geometry"),
        SecondarLines.secondary_line_id,
        SecondarLines.from_node,
        SecondarLines.to_node,
        SecondarLines.conductor_type,
        SecondarLines.description,
        SecondarLines.length_meters,
        SecondarLines.village,
        SecondarLines.municipality,
        SecondarLines.isactive
    ))

    secondar_lines_feat = {
        "secondary_line":[
            Feature(
                id=sl_id,
                geometry=loads(sl_geom),
                properties=dict(
                    line_id = sl_line_id,
                    from_node = sl_from_node,
                    to_node = sl_to_node,
                    conductory_type = sl_conductor_type,
                    description = sl_description,
                    length_meters = float(sl_length_meters),
                    village = sl_village,
                    municipality = sl_municipality,
                    isactive = sl_isactive
                )
            )
            for 
            sl_id, 
            sl_geom,
            sl_line_id, 
            sl_from_node, 
            sl_to_node,
            sl_conductor_type, 
            sl_description, 
            sl_length_meters, 
            sl_village, 
            sl_municipality, 
            sl_isactive
            in secondary_line_data
        ]
    }


    consumer_data = await supassession.exec(
        select(
        Consumer.id,
        functions.ST_AsGeoJSON(Consumer.geom).label("geometry"),
        Consumer.consumer_id,
        Consumer.consumer_name,
        Consumer.consumer_type,
        Consumer.meter_brand,
        Consumer.meter_number,
        Consumer.village,
        Consumer.municipality,
        Consumer.isactive
        ).order_by(asc(Consumer.id))
    )
    consumert_feat = {"consumer":[
        Feature(
            id=id,
            geometry=loads(geometry),
            properties=dict(
                account_no = consumer_id,
                name = consumer_name,
                type = consumer_type,
                brand = meter_brand,
                serial_number = meter_number,
                village = village,
                municipality = municipality,
                status = isactive
            )
        ) for 
        id, geometry, consumer_id, consumer_name,  consumer_type, meter_brand, meter_number, village, municipality, isactive  in consumer_data
    ]}

    return FeatureCollection(features=[sub_feat,pl_feat, transformer_feat, secondar_lines_feat, consumert_feat])

@map_router.get("/mapdata")
async def get_data(session:AsyncSession = supasessionDep):
    data = await get_mapdata(session)
    return data

# REAL-TIME MAP WEBSOCKETE DATA
@map_router.websocket("/ws/mapdata")
async def get_latest_substation(websocket:WebSocket):
    await websocket.accept()
    origin = websocket.headers.get("origin")
    if origin != ORIGIN:
        await websocket.close()
        return
    # INITIAL DATA
    try:
        async with AsyncSession(Db().supa_engine) as session:
            feat = await get_mapdata(session)

        await websocket.send_json(feat)
        await manager.add(websocket)
        while True:
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
   
# UPDATE SUBSTATION AND BROADCAST THE CHANGE
@map_router.post("/update/substation")
async def update_substation(supassession:AsyncSession = supasessionDep,
                            substation_name:str = Form(),
                            substation_status:bool = Form()):
    stmt = await supassession.exec(select(Substation).where(Substation.generator_name == substation_name))
    substation = stmt.one()
    substation.isactive = substation_status
    supassession.add(substation)
    await supassession.commit()
    await supassession.refresh(substation)
    feat = await get_mapdata(supassession)
    cons = await get_inactive_consumer(supassession)
    await manager.broadcast_json(feat)
    await manager.broadcast_json(cons)

@map_router.post("/update/distribution_transformer")
async def update_dt(supassession:AsyncSession = supasessionDep, transformer_id:str= Form(), status:bool = Form()):
    stmt = await supassession.exec(select(DistributionTransformer).where(DistributionTransformer.transformer_id == transformer_id))
    transformer = stmt.one()
    transformer.isactive = status
    try:
        supassession.add(transformer)
        await supassession.commit()
        await supassession.refresh(transformer)
    except Exception as e:
        await supassession.rollback()
        raise HTTPException(404,str(e))
    
    feat = await get_mapdata(supassession)
    cons = await get_inactive_consumer(supassession)
    await manager.broadcast_json(feat)
    await manager.broadcast_json(cons)
    return {"status": "complete"}

    
