from pydantic import BaseModel, Field


class FlowDataSchema(BaseModel):
    flow_name: str = Field(description="Name of the flow")
    flow_id: str = Field(description="ID of the flow")
