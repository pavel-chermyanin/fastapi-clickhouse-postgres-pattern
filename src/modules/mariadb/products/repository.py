from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repository import BaseRepository
from src.modules.mariadb.products.models import Product
from src.modules.mariadb.products.schemas import ProductCreate, ProductUpdate


class ProductRepository(BaseRepository[Product]):
    async def create(self, db: AsyncSession, *, obj_in: ProductCreate) -> Product:
        db_obj = Product(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, *, db_obj: Product, obj_in: ProductUpdate) -> Product:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field in obj_data:
            setattr(db_obj, field, obj_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, db_obj: Product) -> Product:
        await db.delete(db_obj)
        await db.commit()
        return db_obj


product_repository = ProductRepository(Product)
