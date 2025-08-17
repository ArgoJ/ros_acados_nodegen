from typing import Any
from pydantic import BaseModel, Field


class ParameterContext(BaseModel):
    name: str          = "my_parameter"
    type: str          = "float"
    default: Any       = 0.0
    description: str   = "A parameter for my package"

class SubscriberContext(BaseModel):
    name: str          = "my_subscriber"
    topic: str         = "my_topic"
    msg_type: str      = "std_msgs/String"
    callback: str      = "my_callback"
    description: str   = "A subscriber for my package"

class PublisherContext(BaseModel):
    name: str          = "my_publisher"
    topic: str         = "my_topic"
    msg_type: str      = "std_msgs/String"
    queue_size: int    = 10
    description: str   = "A publisher for my package"

class RosContext(BaseModel):
    node_name: str = "generated_node"
    parameters: list[ParameterContext] = Field(default_factory=list)
    subscribers: list[SubscriberContext] = Field(default_factory=list)
    publishers: list[PublisherContext] = Field(default_factory=list)