from fastapi import APIRouter, Depends, WebSocket, Form, WebSocketDisconnect
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, asc
from ..db.sessesion import Db
from ..db.supa_model import PrimaryLines, Substation, DistributionTransformer
from geoalchemy2 import functions
from geojson import Point, FeatureCollection, Feature, loads, load
from ..sockets.ws import ConnectionManager
import asyncio
import json

map_router = APIRouter()
# ASYNC FUNCTION TO YIEL SESSION
async def get_suppasession():
    async with AsyncSession(Db().supa_engine) as session:
        yield session

supasessionDep = Depends(get_suppasession)

# WEB SOCKET MANAGER
manager = ConnectionManager()

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
                                                      ))
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
              ) for dt_id, dt_geom , dt_name, dt_descripiton, dt_transformer_type, dt_village, dt_municipality, dt_image, dt_isactive in transformer_data
        ]
    }
    return FeatureCollection(features=[sub_feat,pl_feat, transformer_feat])

@map_router.get("/mapdata")
async def get_data(session:AsyncSession = supasessionDep):
    data = await get_mapdata(session)
    return data

# REAL-TIME MAP WEBSOCKETE DATA
@map_router.websocket("/ws/mapdata")
async def get_latest_substation(websocket:WebSocket, supasession:AsyncSession = supasessionDep):
    await manager.connect(websocket)
    # INITIAL DATA 
    feat = await get_mapdata(supasession)
    await manager.broadcast_json(feat)
    try:
        while True:
            await asyncio.sleep(1)
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
    await manager.broadcast_json(feat)
       
         
        


    
