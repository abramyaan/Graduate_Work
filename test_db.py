import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect('postgresql://user@127.0.0.1:5433/resume_db')
    print('OK')
    await conn.close()

asyncio.run(test())