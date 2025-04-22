from marshmallow import Schema, fields, validate


class AdminRequestSchema(Schema):
    email = fields.Str(
        required=True,
        validate=validate.Email(),
        error_messages={
            "required": "Email is required",
            "invalid": "Invalid email format"
        }
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={
            "required": "Password is required",
            "invalid": "Password must be at least 8 characters"
        }
    )


class AdminResponseSchema(Schema):
    id = fields.Int()
    email = fields.Email()


class ThemeRequestShemaPost(Schema):
    theme = fields.Str(
        required=True,
        validate=validate.Length(min=3),
        error_messages={
            "required": "Theme name is required",
            "invalid": "Theme name must be at least 3 characters"
        }
    )


class ThemeResponse(Schema):
    id = fields.Int()
    theme_name = fields.Str()


class ListThemeResponse(Schema):
    themes = fields.Nested(ThemeResponse, many=True)


class QuestionRequestShemaPost(Schema):
    theme_name = fields.Str(required=True)
    question_text = fields.Str(
        required=True,
        validate=validate.Length(min=10)
    )
    question_price = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )


class QuestionResponse(Schema):
    id = fields.Int()
    theme_id = fields.Int()
    price = fields.Int()
    question_text = fields.Str()


class UserStatsResponse(Schema):
    user_id = fields.Int()
    total_score = fields.Int()
    total_games = fields.Int()
    total_wins = fields.Int()


class ErrorResponse(Schema):
    status = fields.Str()
    message = fields.Str()
    data = fields.Dict()