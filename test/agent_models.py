from uagents import Model

class Message(Model):
    message: str
    field: int = 0  # Optional field with default value 