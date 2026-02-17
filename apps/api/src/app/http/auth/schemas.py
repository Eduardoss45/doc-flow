from marshmallow import Schema, fields


class ClientIdResponseSchema(Schema):
    status = fields.Str(required=True)
    client_id = fields.Str()
    expires_at = fields.DateTime()
    expires_in_seconds = fields.Int()
