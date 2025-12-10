from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from sqlmodel import select, asc
from sqlmodel.ext.asyncio.session import AsyncSession
from ..db.sessesion import Db
from ..db.supa_model import Consumer
from ..sockets.ws import manager
import asyncio

dashboard_router = APIRouter()


async def get_supassesion():
    async with AsyncSession(Db().supa_engine) as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
        finally:
            await session.close()

supassesiondep = Depends(get_supassesion)

async def get_inactive_consumer(session:AsyncSession):
    
    stmt = await session.exec(select(Consumer).where(Consumer.isactive == False).order_by(asc(Consumer.id)))
    consumer_data = [
            dict(
                id = val.id,
                account_no = val.consumer_id,
                consumer_name = val.consumer_name,
                type = val.consumer_type,
                brand = val.meter_brand,
                serial_no = val.meter_number,\
                village = val.village,
                municipality = val.municipality
                ) for val in
        stmt.all()]
    return {
        "type": "dashboard",
        "inactive_consumer": consumer_data 
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
        

    
