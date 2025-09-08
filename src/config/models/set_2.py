from pydantic import BaseModel

# Set 2 - Plan de razonamiento
# - introduccion: tipo str, obligatorio - fundamentos del tipo de validación realizada

class Set2ExtractionModel(BaseModel):
    pass

class Set2RenderingModel(BaseModel):
    introduccion: str

class Set2StructuredOutputSupervisor(BaseModel):
    introduccion: str