
import aiosqlite


class SQLiteStorage:
    def __init__(self, db_path: str = "bot_session.db") -> None:
        self.db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._db = await aiosqlite.connect(self.db_path)
        await self._db.execute("PRAGMA journal_mode=WAL")

        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS session_data (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS megolm_sessions (
                room_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                sender_key TEXT NOT NULL,
                pickle TEXT NOT NULL,
                PRIMARY KEY (room_id, session_id)
            )
            """
        )

        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS megolm_outbound (
                room_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                pickle TEXT NOT NULL,
                message_count INTEGER NOT NULL DEFAULT 0,
                created_at INTEGER NOT NULL
            )
            """
        )

        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS olm_sessions (
                sender_key TEXT NOT NULL,
                session_id TEXT NOT NULL,
                pickle TEXT NOT NULL,
                PRIMARY KEY (sender_key, session_id)
            )
            """
        )

        await self._db.commit()

    def _require_db(self) -> aiosqlite.Connection:
        if self._db is None:
            raise RuntimeError("Storage is not connected. Call connect() first.")
        return self._db

    async def set(self, key: str, value: str) -> None:
        db = self._require_db()
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
        db = self._require_db()
        async with db.execute("SELECT value FROM session_data WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

    async def delete(self, key: str) -> None:
        db = self._require_db()
        await db.execute("DELETE FROM session_data WHERE key = ?", (key,))
        await db.commit()

    async def store_megolm_session(
        self, room_id: str, session_id: str, sender_key: str, pickle: str
    ) -> None:
        db = self._require_db()
        await db.execute(
            """
            INSERT INTO megolm_sessions (room_id, session_id, sender_key, pickle)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(room_id, session_id) DO UPDATE SET pickle = excluded.pickle
            """,
            (room_id, session_id, sender_key, pickle),
        )
        await db.commit()

    async def get_megolm_session(self, room_id: str, session_id: str) -> str | None:
        db = self._require_db()
        async with db.execute(
            "SELECT pickle FROM megolm_sessions WHERE room_id = ? AND session_id = ?",
            (room_id, session_id),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

    async def get_all_megolm_sessions(self, room_id: str) -> list[tuple[str, str, str]]:
        """Возвращает [(session_id, sender_key, pickle), ...] для комнаты."""
        db = self._require_db()
        async with db.execute(
            "SELECT session_id, sender_key, pickle FROM megolm_sessions WHERE room_id = ?",
            (room_id,),
        ) as cursor:
            return await cursor.fetchall()

    async def store_outbound_session(
        self, room_id: str, session_id: str, pickle: str, message_count: int, created_at: int
    ) -> None:
        db = self._require_db()
        await db.execute(
            """
            INSERT INTO megolm_outbound (room_id, session_id, pickle, message_count, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(room_id) DO UPDATE SET
                session_id = excluded.session_id,
                pickle = excluded.pickle,
                message_count = excluded.message_count,
                created_at = excluded.created_at
            """,
            (room_id, session_id, pickle, message_count, created_at),
        )
        await db.commit()

    async def get_outbound_session(self, room_id: str) -> tuple[str, str, int, int] | None:
        """Возвращает (session_id, pickle, message_count, created_at) либо None."""
        db = self._require_db()
        async with db.execute(
            "SELECT session_id, pickle, message_count, created_at FROM megolm_outbound WHERE room_id = ?",
            (room_id,),
        ) as cursor:
            return await cursor.fetchone()

    async def delete_outbound_session(self, room_id: str) -> None:
        db = self._require_db()
        await db.execute("DELETE FROM megolm_outbound WHERE room_id = ?", (room_id,))
        await db.commit()

    async def store_olm_session(self, sender_key: str, session_id: str, pickle: str) -> None:
        db = self._require_db()
        await db.execute(
            """
            INSERT INTO olm_sessions (sender_key, session_id, pickle)
            VALUES (?, ?, ?)
            ON CONFLICT(sender_key, session_id) DO UPDATE SET pickle = excluded.pickle
            """,
            (sender_key, session_id, pickle),
        )
        await db.commit()

    async def get_olm_sessions(self, sender_key: str) -> list[tuple[str, str]]:
        """Возвращает [(session_id, pickle), ...] для данного sender_key устройства."""
        db = self._require_db()
        async with db.execute(
            "SELECT session_id, pickle FROM olm_sessions WHERE sender_key = ?",
            (sender_key,),
        ) as cursor:
            return await cursor.fetchall()

    async def close(self) -> None:
        if self._db is not None:
            await self._db.close()
            self._db = None
