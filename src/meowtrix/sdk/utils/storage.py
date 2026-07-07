import aiosqlite


class SQLiteStorage:
    def __init__(self, db_path: str = "bot_session.db") -> None:
        self.db_path = db_path

    async def connect(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS session_data (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            await db.commit()

    async def set(self, key: str, value: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO session_data (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )
            await db.commit()

    async def get(self, key: str) -> str | None:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT value FROM session_data WHERE key = ?", (key,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def delete(self, key: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM session_data WHERE key = ?", (key,))
            await db.commit()
