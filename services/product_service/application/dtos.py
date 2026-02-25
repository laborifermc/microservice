from pydantic import BaseModel

class ProductCreateDTO(BaseModel):
    name: str
    description: str
    category: str