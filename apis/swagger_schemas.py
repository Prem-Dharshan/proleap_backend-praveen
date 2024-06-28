from drf_yasg import openapi

# Define the schema for the Answer model
answer_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'answer': openapi.Schema(type=openapi.TYPE_STRING),
        'user': openapi.Schema(type=openapi.TYPE_INTEGER),
        'question': openapi.Schema(type=openapi.TYPE_INTEGER),
        'option': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
    }
)

# Define the schema for the Option model
option_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'value': openapi.Schema(type=openapi.TYPE_STRING),
        'sequence_no': openapi.Schema(type=openapi.TYPE_INTEGER),
        'question': openapi.Schema(type=openapi.TYPE_INTEGER),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
    }
)

# Define the schema for the Question model
question_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'text': openapi.Schema(type=openapi.TYPE_STRING),
        'type': openapi.Schema(type=openapi.TYPE_STRING),
        'desc': openapi.Schema(type=openapi.TYPE_STRING),
        'is_required': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'card': openapi.Schema(type=openapi.TYPE_INTEGER),
        'sequence_no': openapi.Schema(type=openapi.TYPE_INTEGER),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'options': openapi.Schema(type=openapi.TYPE_ARRAY, items=option_schema),
        'answers': openapi.Schema(type=openapi.TYPE_ARRAY, items=answer_schema),
    }
)

# Define the schema for the UserCard model
user_card_progress_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'card_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'completed_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
        'status': openapi.Schema(type=openapi.TYPE_STRING),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
    }
)

# Define the schema for the Card model
card_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'desc': openapi.Schema(type=openapi.TYPE_STRING),
        'type': openapi.Schema(type=openapi.TYPE_STRING),
        'to_be_shown': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'start_time': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'end_time': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'duration': openapi.Schema(type=openapi.TYPE_STRING),
        'total_questions': openapi.Schema(type=openapi.TYPE_INTEGER),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'activity': openapi.Schema(type=openapi.TYPE_INTEGER),
        'sequence_no': openapi.Schema(type=openapi.TYPE_INTEGER),
        'user_card_progress': user_card_progress_schema,
        'questions': openapi.Schema(type=openapi.TYPE_ARRAY, items=question_schema),
    }
)

user_activity_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
        "activity_id": openapi.Schema(type=openapi.TYPE_INTEGER),
        "user_id": openapi.Schema(type=openapi.TYPE_INTEGER),
        "completed_cards": openapi.Schema(type=openapi.TYPE_INTEGER),
        "status": openapi.Schema(type=openapi.TYPE_STRING),
        "created_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        "updated_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
    })


activity_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
        "name": openapi.Schema(type=openapi.TYPE_STRING),
        "desc": openapi.Schema(type=openapi.TYPE_STRING),
        "start_time": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        "end_time": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        "total_cards": openapi.Schema(type=openapi.TYPE_INTEGER),
        "total_polling_cards": openapi.Schema(type=openapi.TYPE_INTEGER),
        "created_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        "updated_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        "batch": openapi.Schema(type=openapi.TYPE_INTEGER),
        "sequence_no": openapi.Schema(type=openapi.TYPE_INTEGER),
        "user_activity_progress": user_activity_schema
    }

)


# Define the schema for the overall response
activity_answer_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'recent_card_id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'cards': openapi.Schema(type=openapi.TYPE_ARRAY, items=card_schema),
    }
)

batch_activity_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT, properties={
        'current_activity_id': openapi.Schema(
            type=openapi.TYPE_INTEGER), 'activities': openapi.Schema(
                type=openapi.TYPE_ARRAY, items=activity_schema), })
