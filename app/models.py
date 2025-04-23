from typing import List, Optional

from pydantic import BaseModel


class SearchGoogleMapsResponseItem(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    phone_number: Optional[str] = None
    schedule: Optional[str] = None
    
class SearchGoogleMapsResponse(BaseModel):
    items: List[SearchGoogleMapsResponseItem] = []