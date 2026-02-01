from uuid import UUID
from pathlib import Path

from src.domain.entities import DocumentJob
from src.domain.enums import ConversionType
from src.repositories.document_repository import DocumentRepository


class DocumentService:
    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    def create_job(
        self,
        conversion_type: ConversionType,
        input_path: str,
    ) -> DocumentJob:
        """
        Cria um job de conversão de documento.
        - instancia o domínio
        - persiste o estado inicial
        - retorna o job criado
        """
        job = DocumentJob(conversion_type=conversion_type, input_path=input_path)
        self.repository.save(job)
        return job
