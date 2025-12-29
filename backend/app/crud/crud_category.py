from sqlmodel import Session, select
from app.models.lab import Category
from typing import List


def get_all(session: Session) -> List[Category]:
    # 按 sort_order 排序返回
    statement = select(Category).order_by(
        Category.sort_order.asc(),
        Category.id.asc()
    )
    return session.exec(statement).all()

def get_by_id(session: Session, category_id: int) -> Category | None:
    return session.get(Category,category_id)