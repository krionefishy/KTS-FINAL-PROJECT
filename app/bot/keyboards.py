from app.store.database.modles import Answer, Theme


def create_join_kb() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "Присоединиться", "callback_data": "join_game"}]
        ]
    }


def create_theme_kb(topics: list[Theme]) -> dict:
    return {
        "inline_keyboard": [
            [{"text": topic.theme_name,
              "callback_data": f"theme:{topic.id}"
            }]
            for topic in topics
        ]
    }


def create_question_kb(questions: list[int], ) -> dict:
    return {
        "inline_keyboard": [
            [{"price": price, "callback_data": f"question:{price}"}] 
            for price in questions
        ]
    }


def create_answers_kb(answer: Answer) -> dict:
    return {
        "inline_keyboard": [
            [{
                "text": answer_text,
                "callback_data": f"answer:{answer.question_id}:{idx}"
            }]
            for idx, (answer_text, _) in enumerate(answer.items())
        ]
    }