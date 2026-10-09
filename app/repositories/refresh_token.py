"""Репозиторий для одноразовых refresh-токенов."""

from datetime import datetime

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    @property
    def model(self) -> type[RefreshToken]:
        return RefreshToken

    async def consume(
        self,
        jti: str,
        user_id: int,
        now: datetime,
    ) -> bool:
        """Атомарно помечает токен отозванным, только если он еще действителен."""
        result = await self.session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.jti == jti,
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > now,
            )
            .values(revoked_at=now)
        )
        return result.rowcount == 1
