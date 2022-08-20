from enum import Enum

from django.db import models

class TableFieldType(Enum):
    NUMBER = "number"
    TEXT = "text"
    IMAGE = "image"
    DATE = "date"
    PRICE = "price"
    BOOLEAN = "boolean"

class TableHeading():

    def __init__(self, display: str, field: str, fieldType: TableFieldType):
        self.display = display
        self.field = field
        self.fieldType = fieldType

    def serialize(self):
        return {
            "display": self.display, "field": self.field, "type": self.fieldType.value
        }

class TableSerializableModel(models.Model):

    class Meta:
        abstract = True

    @staticmethod
    def get_table_headings():
        return [
            TableHeading("PK", "pk", TableFieldType.NUMBER)
        ]

    @classmethod
    def get_serialized_table_headings(cls):
        return [h.serialize() for h in cls.get_table_headings()]

    @classmethod
    def get_table_rows(cls):
        fields = [heading.field for heading in cls.get_table_headings()] + ["pk"]

        objects = cls.objects.all()
        if len(objects) == 0: return []

        serialized = []

        for object in objects:
            object_dict = object.__dict__

            serialized_object = {}
            for field in fields:
                serialized_object[field] = object_dict[field] if field in object_dict else None

            # add pk
            serialized_object["pk"] = object.pk

            serialized.append(serialized_object)
        return serialized