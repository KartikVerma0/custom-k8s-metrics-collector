from pydantic import BaseModel

class NodeMetrics(BaseModel):
    metadata: object
    timestamp: str
    window: str
    usage: object

class NodeMetricsList(BaseModel):
    kind: str
    apiVersion: str
    metadata: object
    items: list[NodeMetrics]


