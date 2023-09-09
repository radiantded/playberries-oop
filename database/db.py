import aiosqlite as sql


class Database:
    async def __aenter__(self):
        self.db = await sql.connect('base.db')
        self.cursor = await self.db.cursor()
        await self.create_table()
        return self

    async def __aexit__(self, *args):
        await self.cursor.close()
        await self.db.close()

    async def create_table(self):
        await self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS
            tasks(
                task_id INTEGER PRIMARY KEY,
                prompt TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                operations INTEGER,
                cart_rate INTEGER
            )
        """)
        await self.db.commit()

    async def add(self, data: tuple):
        await self.cursor.execute("""
            INSERT INTO 
            tasks (prompt, product_id, operations, cart_rate)
            VALUES (?, ?, ?, ?)
            RETURNING task_id
        """, data)
        id_ = await self.cursor.fetchone()
        await self.db.commit()
        return id_

    async def get_all(self):
        result = await self.cursor.execute("""
            SELECT * FROM tasks
        """)
        all = await result.fetchall()
        return all

    async def get_one(self, id_: int):
        result = await self.cursor.execute("""
            SELECT * FROM tasks
            WHERE task_id = ?
        """, (id_, ))
        one = await result.fetchone()
        return one

    async def delete(self, id_: int):
        await self.cursor.execute("""
            DELETE FROM tasks
            WHERE task_id = ?
        """, (id_, ))
        await self.db.commit()
