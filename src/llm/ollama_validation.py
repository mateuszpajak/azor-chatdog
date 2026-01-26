from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
import os

class OllamaConfig(BaseModel):
    engine: Literal["OLLAMA"] = Field(default="OLLAMA")
    model_name: str = Field(..., description="Nazwa modelu uruchomionego na lokalnym serwerze Ollama")
    base_url: str = Field("http://localhost:11434/v1", description="URL lokalnego serwera Ollama")
    temperature: Optional[float] = Field(None, description="Wartość parametru temperature")
    top_p: Optional[float] = Field(None, description="Wartość parametru top_p")

    @validator('model_name')
    def validate_model_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError("model_name musi być zdefiniowany")
        return v.strip()