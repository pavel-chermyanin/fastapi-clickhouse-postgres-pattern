from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.mariadb.products.models import Product
from src.modules.mariadb.products.repository import product_repository
from src.modules.mariadb.products.schemas import ProductCreate, ProductUpdate


class ProductService:
    async def get_product(self, db: AsyncSession, product_id: int) -> Optional[Product]:
        return await product_repository.get(db, product_id)

    async def get_products(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        return await product_repository.get_multi(db, skip=skip, limit=limit)

    async def create_product(self, db: AsyncSession, product_in: ProductCreate) -> Product:
        return await product_repository.create(db, obj_in=product_in)

    async def update_product(
        self, db: AsyncSession, product_id: int, product_in: ProductUpdate
    ) -> Optional[Product]:
        product = await product_repository.get(db, product_id)
        if not product:
            return None
        return await product_repository.update(db, db_obj=product, obj_in=product_in)

    async def delete_product(self, db: AsyncSession, product_id: int) -> Optional[Product]:
        product = await product_repository.get(db, product_id)
        if not product:
            return None
        return await product_repository.delete(db, db_obj=product)


product_service = ProductService()
