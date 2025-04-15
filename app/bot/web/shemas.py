from marshmallow import Schema, fields, validate


class RespShema(Schema):
    status = fields.Int()
    data = fields.Dict()


class AdminRequestShema(Schema):
    email = fields.Str(
        required=True,
        error_messages={
            "required": "email должен быть передан",
        }
    )

    password = fields.Str(
        required=True, 
        validate=validate.Length(min=8, max=100),
        error_messages={
            "required": "Password is required",
            "invalid": "Password must be 8-100 characters"
        }
    )


class ThemeRequestShemaPost(Schema):
    theme = fields.Str(
        required=True,
        error_messages={
            "required": "тема должна быть передана",
        }
    )


class QuestionRequestShemaPost(Schema):
    theme_name = fields.Str(
        required=True
    )
    quesion_text = fields.Str(
        required=True
    )
    quesion_price = fields.Int()
