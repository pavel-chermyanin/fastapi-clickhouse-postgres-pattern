from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.mariadb.session import get_mariadb_db
from src.modules.mariadb.products.schemas import Product, ProductCreate, ProductUpdate
from src.modules.mariadb.products.service import product_service

router = APIRouter()


@router.get("/", response_model=List[Product])
async def read_products(
    db: AsyncSession = Depends(get_mariadb_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Получение списка продуктов.
    """
    return await product_service.get_products(db, skip=skip, limit=limit)


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    *,
    db: AsyncSession = Depends(get_mariadb_db),
    product_in: ProductCreate,
) -> Any:
    """
    Создание нового продукта.
    """
    return await product_service.create_product(db, product_in)


@router.get("/{product_id}", response_model=Product)
async def read_product_by_id(
    product_id: int,
    db: AsyncSession = Depends(get_mariadb_db),
) -> Any:
    """
    Получение информации о конкретном продукте по его ID.
    """
    product = await product_service.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_mariadb_db),
) -> Any:
    """
    Обновление информации о продукте.
    """
    product = await product_service.update_product(db, product_id, product_in)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}", response_model=Product)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_mariadb_db),
) -> Any:
    """
    Удаление продукта.
    """
    product = await product_service.delete_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
