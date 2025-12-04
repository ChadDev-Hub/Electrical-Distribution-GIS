from db.sessesion import Db
import asyncio

async def create_table():
    db_session = Db()
    await db_session.create_supa_table()

if __name__ =="__main__":
    asyncio.run(create_table())



