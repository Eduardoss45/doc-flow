from marshmallow import Schema, fields, validate
from app.domain.enums.conversion_type import ConversionType


class ConversionTypeField(fields.Str):
    def _serialize(self, value, attr, obj, **kwargs):
        return value.value if hasattr(value, "value") else value


class UploadFormSchema(Schema):
    conversion_type = fields.Str(
        required=True,
        validate=validate.OneOf([e.value for e in ConversionType]),
        metadata={"description": "Tipo de conversão desejada"},
    )


class JobCreatedSchema(Schema):
    job_id = fields.Str(required=True)
    status = fields.Str(required=True)
    message = fields.Str(required=True)


class FileItemSchema(Schema):
    filename = fields.Str()
    size_bytes = fields.Int()
    size_mb = fields.Float()
    modified_at = fields.DateTime()
    download_url = fields.Str()
    extension = fields.Str(allow_none=True)


class FileListSchema(Schema):
    client_id = fields.Str()
    count = fields.Int()
    files = fields.List(fields.Nested(FileItemSchema))
    has_more = fields.Bool()
