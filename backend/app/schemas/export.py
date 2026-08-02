from datetime import datetime

from pydantic import BaseModel


class ExportLinkPublic(BaseModel):
    download_url: str
    expires_at: datetime
