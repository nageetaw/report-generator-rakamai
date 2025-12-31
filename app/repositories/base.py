from typing import Generic, TypeVar, Type, Optional, cast, Protocol

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import HTTPException, status


class HasId(Protocol):
    id: str


ModelType = TypeVar("ModelType", bound=HasId)


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.db = db
        self.model = model

    async def get(self, id: str) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        record = result.scalar_one_or_none()
        if record:
            return cast(Optional[ModelType], result.scalar_one_or_none())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Record does not exists."
        )

    async def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, id: str) -> bool:
        obj = await self.get(id)
        if not obj:
            return False
        await self.db.delete(obj)
        await self.db.commit()
        return True
