from fastapi import APIRouter, Depends
from app.models.lab import Category
from sqlmodel import Session
from app.db.session import get_session
from app.services.category_service import CategoryService


router = APIRouter()


@router.get("/",response_model=list[Category])
def read_categories(session: Session = Depends(get_session)):
    return CategoryService.get_sidebar_categories(session)