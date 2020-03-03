import asyncpg


class DatabaseHandler:
    def __init__(self, **kwargs):
        self.con = None
        self.kwargs = kwargs

    async def is_connected(self):
        if self.con is None:
            self.con = await asyncpg.create_pool(**self.kwargs)

    async def execute(self, *args, **kwargs):
        await self.is_connected()
        async with self.con.acquire() as connection:
            async with connection.transaction():
                await connection.execute(*args, **kwargs)

    async def insert(self, table, args: list):
        await self.is_connected()

        marks = ', '.join([f'${_}' for _ in range(1, len(args)+1)])
        async with self.con.acquire() as connection:
            async with connection.transaction():
                await connection.execute(f"INSERT INTO {table} VALUES ({marks})", *args)

    async def get(self, table, select: list, where: dict):
        await self.is_connected()
        async with self.con.acquire() as connection:
            async with connection.transaction():
                safe_select = ", ".join(select)
                safe_where = {}
                for i, (k, v) in enumerate(where.items(), 1):
                    if isinstance(v, list):
                        safe_where[f"{k}{v[0]}${i}"] = v[1]
                        continue
                    safe_where[f"{k}=${i}"] = v

                str_where = " AND ".join(safe_where.keys())
                a = await connection.fetch(f"SELECT {safe_select or '*'} FROM {table}{' WHERE ' + str_where if str_where else ''}", *safe_where.values())
                return a

    async def delete(self, table, _where: dict):
        await self.is_connected()
        async with self.con.acquire() as connection:
            async with connection.transaction():
                where = ' AND '.join([f'{k}=${i}' for i, k in enumerate(_where, 1)])
                await connection.execute(f"DELETE FROM {table} WHERE {where}", *_where.values())

    async def update(self, table, _updated: dict, _where: dict):
        await self.is_connected()
        updated = []
        _i = 1
        for i, column in enumerate(_updated, 1):
            updated.append(f"{column}=${i}")
            _i = i
        updated = ", ".join(updated)
        where = ' AND '.join([f'{k}=${i}' for i, k in enumerate(_where, _i+1)])
        async with self.con.acquire() as connection:
            async with connection.transaction():
                print(f"UPDATE {table} SET {updated} WHERE {where}", *_updated.values(), *_where.values())
                await connection.execute(f"UPDATE {table} SET {updated} WHERE {where}", *_updated.values(), *_where.values())
