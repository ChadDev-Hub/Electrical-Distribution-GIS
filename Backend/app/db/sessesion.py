from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel import SQLModel, text
from . import supa_model
import os
from dotenv import load_dotenv

class Db:
    def __init__(self):
        load_dotenv()
        # LOCAL DATABASE
        LOCAL_DBNAME = os.getenv("LOCALDBNAME")
        LOCAL_USERNAME= os.getenv("LOCALUSER")
        LOCAL_PASSWORD= os.getenv("LOCALPASSWORD")
        HOST_LOCAL= os.getenv("HOSTLOCAL")
        LOCAL_PORT = os.getenv("LOCALPORT")
        self.local_engine = create_async_engine(f"postgresql+asyncpg://{LOCAL_USERNAME}:{LOCAL_PASSWORD}@{HOST_LOCAL}:{LOCAL_PORT}/{LOCAL_DBNAME}")
        
        # SUPABASE
        SUPA_DBNAME = os.getenv("SUPADBNAME")
        SUPA_USER = os.getenv("SUPAUSER")
        SUPA_PORT = os.getenv("SUPAPORT")
        SUPA_HOST = os.getenv("SUPAHOST")
        SUPA_PASSWORD = os.getenv("SUPAPASSWORD")
        self.supa_engine = create_async_engine(f"postgresql+asyncpg://{SUPA_USER}:{SUPA_PASSWORD}@{SUPA_HOST}:{SUPA_PORT}/{SUPA_DBNAME}")
        
    async def create_local_table(self):
       async with self.local_engine.begin() as conn:
           await conn.run_sync(SQLModel.metadata.create_all)
           
    async def create_supa_table(self):
        async with self.supa_engine.begin() as conn:
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS gis;"))
            await conn.run_sync(supa_model.supa_meta_data.create_all)
            for functrig in [
                supa_model.update_village_municipality,
                supa_model.trigger_village_municipality,
                supa_model.is_node_active,
                supa_model.node_status_update_trigger,
                supa_model.nodes_trigger,
                supa_model.update_franchise_area_id,
                supa_model.trigger_update_franchise_area_id,
                supa_model.nodes_substation_function,
                supa_model.nodes_substation_id_trigger,
                supa_model.update_primary_line,
                supa_model.update_primary_line_trigger,
                supa_model.update_node_substation_id,
                supa_model.update_node_substation_id_trigger,
                supa_model.line_bushing_update,
                supa_model.line_bushing_trigger,
                supa_model.line_bushing_after_update,
                supa_model.line_bushing_after_trigger
                
            ]:
               await conn.execute(functrig)
            
   