from typing import List
from sqlmodel import Session
from app.crud import crud_category
from app.models.lab import Category


class CategoryService:
    @staticmethod
    def get_sidebar_categories(session: Session) -> List[Category]:
        return crud_category.get_all(session)