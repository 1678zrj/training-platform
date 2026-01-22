import os
from sqlmodel import Session
from app.models.lab import ExperimentResource


class ExperimentResourceService:

    @staticmethod
    def get_file_content(resource_id: int,session: Session):
        resource = session.get(ExperimentResource, resource_id)
        full_path = os.path.join(os.getcwd(), "media", resource.file_path_or_url.lstrip("/"))
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
