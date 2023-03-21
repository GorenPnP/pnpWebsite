from enum import Enum

class TableFieldType(Enum):
    NUMBER = "number"
    TEXT = "text"
    IMAGE = "image"
    DATE = "date"
    DATE_TIME = "datetime"
    PRICE = "price"
    BOOLEAN = "boolean"

    NUMBER_INPUT = "number input"

class TableHeading():

    def __init__(self, display: str, field: str, fieldType: TableFieldType):
        self.display = display
        self.field = field
        self.fieldType = fieldType

    def serialize(self):
        return {
            "display": self.display, "field": self.field, "type": self.fieldType.value
        }
