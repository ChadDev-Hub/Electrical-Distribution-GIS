from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from sqlmodel import select, asc, func, case, not_, and_
from sqlmodel.ext.asyncio.session import AsyncSession
from ..db.sessesion import Db
from ..db.supa_model import Consumer, Substation, PrimaryLines, SecondarLines, DistributionTransformer
from ..sockets.ws import manager
import asyncio

dashboard_router = APIRouter()


async def get_supassesion():
    async with AsyncSession(Db().supa_engine) as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            print(e)
            raise
        finally:
            await session.close()

supassesiondep = Depends(get_supassesion)

async def get_inactive_consumer(session:AsyncSession):
    # GET ALL CONSUMER WITH INACTIVE CONNECTION
    stmt = await session.exec(select(Consumer).where(Consumer.isactive == False).order_by(asc(Consumer.id)))
    consumer_data = [
            dict(
                id = val.id,
                account_no = val.consumer_id,
                consumer_name = val.consumer_name,
                type = val.consumer_type,
                brand = val.meter_brand,
                serial_no = val.meter_number,
                village = val.village,
                municipality = val.municipality
                ) for val in
        stmt.all()]
    
    # GET THE TOTAL CONSUMER 
    total_consumer_stmt = await session.exec(
        select(
            func.sum(case((Consumer.isactive, 1), else_=0)).label("active"),
            func.sum(case((not_(Consumer.isactive), 1), else_=0)).label("inactive"),
            func.count().label("total")
            )
     )
    row = total_consumer_stmt.fetchall()
    active, inactive, total =row[0]
    total_consumer = [
        {   "label": "Active",
            "count": active,
            "color": "green"
        },
        { "label": "Inactive",
           "count": inactive,
           "color": "red"
        },
        {
           "label": "Total",
           "count":  total,
           "color": "blue"
        }
        ]
    
    # TOTAL PRIMARY LINE LENGTH BY PHASING AND BY SUBSTATION
    total_pl_length_stmt = await session.exec(select(Substation.generator_name,
                                                     func.sum(case((func.char_length(PrimaryLines.phasing)==2,PrimaryLines.length),else_=0)).label("single_phase"),
                                                     func.sum(case((func.char_length(PrimaryLines.phasing) == 3, PrimaryLines.length), else_=0)).label("v_phase"),
                                                     func.sum(case((func.char_length(PrimaryLines.phasing) == 4, PrimaryLines.length), else_=0)).label("three_phase"))
                                                     .join(Substation, Substation.id == PrimaryLines.substation_id)
                                                     .group_by(Substation.generator_name)
                                                     .order_by(Substation.generator_name))
    # DATA STRUCTURE FOR PIE CHART
    primary_line_length = [
        {
          
                "substation": substation,
                "series":[{
                    "innerRadius":20,
                    "highlightScope":{
                        "fade": 'global',
                        "highlight":"item"
                    },
                    "faded":{
                        "innerRadius":30,
                        "additionalRadius": -30,
                        "color": 'grey'
                             },
                    "data":[
                        {
                                "label" : "Single Phase",
                                "value": float(single_phase),
                                "color": "red"
                        },
                        {
                            "label": "V Phase",
                            "value": float(v_phase),
                            "color": "blue"
                        },
                        {
                            "label": "Three Phase",
                            "value": float(three_phase),
                            "color": "green"
                        }]
                }]
        }for 
        substation, single_phase, v_phase, three_phase in total_pl_length_stmt.fetchall()]
    
    sl_stmt = await session.exec(select(
                                Substation.generator_name,
                                func.sum(case((SecondarLines.description == "UNDER-BUILT", SecondarLines.length_meters), else_=0)).label("ub_total"),
                                func.sum(case((SecondarLines.description == "OPEN-SECONDARY", SecondarLines.length_meters), else_=0)).label("os_total"),
                                func.sum(case((and_(SecondarLines.description == "UNDER-BUILT", func.char_length(SecondarLines.phasing) == 2), SecondarLines.length_meters), else_=0)).label("ub_single_phase"),
                                func.sum(case((and_(SecondarLines.description == "UNDER-BUILT", func.char_length(SecondarLines.phasing) == 3), SecondarLines.length_meters), else_=0)).label("ub_vphase"),
                                func.sum(case((and_(SecondarLines.description == "UNDER-BUILT", func.char_length(SecondarLines.phasing) == 4), SecondarLines.length_meters), else_=0)).label("ub_three_phase"),
                                func.sum(case((and_(SecondarLines.description == "OPEN-SECONDARY",func.char_length(SecondarLines.phasing) == 2), SecondarLines.length_meters), else_=0)).label("os_single_phase"),
                                func.sum(case((and_(SecondarLines.description == "OPEN-SECONDARY",func.char_length(SecondarLines.phasing) == 3), SecondarLines.length_meters), else_=0)).label("os_v_phase"),
                                func.sum(case((and_(SecondarLines.description == "OPEN-SECONDARY",func.char_length(SecondarLines.phasing) == 4), SecondarLines.length_meters), else_=0)).label("os_three_phase"))
                                 .join(DistributionTransformer,SecondarLines.dt_id == DistributionTransformer.transformer_id)
                                 .join(Substation, Substation.id == DistributionTransformer.substation_id)
                                 .group_by(Substation.generator_name))
    sl_data = [{
        "substation_id": substation_id,
        "series":[

            {
                "innerRadius": 15,
                "outerRadius": 50,
                "data": [{
                    "label" : "Under Built Total",
                    "value" : float(ub_total),
                    "color": "yellow"},
                    {"label": "Open Secondary Total",
                    "value": float(os_total),
                    "color": "orange"}
                    ],
                "highlightScope": { "fade": 'global', "highlight": 'item' }
            },
            {
                "id": 'outer',
                "innerRadius": 50,
                "outerRadius": 100,
                "data":[
            {
            "label": "Ub Single Phase",
            "value": float(ub_single),
            "color":"yellow"
            },
            {
            "label": "Ub V Phase",
            "value": float(ub_v),
            "color":"yellow"
            },
            
            {
            "label": "Ub three Phase",
            "value": float(ub_three),
            "color":"yellow"
            },
            {
                "label": "Os Single Phase",
                "value": float(os_single),
                "color":"orange"
            },
            {
                "label": "Os V Phase",
                "value": float(os_v),
                "color":"orange"
            },
            {
                "label": "OS Three",
                "value": float(os_three),
                "color":"orange"
            }],
            "highlightScope": { "fade": 'global', "highlight": 'item' }}
        ]} for substation_id,ub_total,os_total, ub_single, ub_v, ub_three, os_single, os_v, os_three in sl_stmt.fetchall()]
    
    return {
        "type": "dashboard",
        "inactive_consumer": consumer_data,
        "total_consumer": total_consumer,
        "primary_line_length": primary_line_length,
        "secondary_line_length": sl_data
    }


@dashboard_router.websocket("/ws/dashboard")
async def get_data(socket:WebSocket, supassession:AsyncSession = supassesiondep):
    await manager.connect(socket)
    try:
        inaactive_cons = await get_inactive_consumer(supassession)
        await manager.broadcast_json(inaactive_cons)
        while True:
            await asyncio.sleep(3)

    except WebSocketDisconnect:
        await manager.disconnect(socket)
        

    
@dashboard_router.get("/dashboard/data")
async def get_dashboard_data(supassession:AsyncSession= supassesiondep):
    data = await get_inactive_consumer(supassession)
    return JSONResponse(data)
