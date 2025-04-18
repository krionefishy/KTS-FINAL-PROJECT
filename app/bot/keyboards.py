from app.store.database.modles import Answer


def create_join_kb(chat_id: int) -> dict:
    return {
        "inline_keyboard": [
            [{"text": "Присоединиться", "callback_data": f"join:{chat_id}"}]
        ]
    }


def create_theme_kb(topics: list[str]) -> dict:
    return {
        "inline_keyboard": [
            [{"text": topic, "callback_data": f"topic {topic}"}] for topic in topics
        ]
    }


def create_question_kb(questions: list[int]) -> dict:
    # TODO подумать, какой колбек ставить вопросам, так как берем их из базы в моменте
    return {
        "inline_keyboard": [
            [{"price": price, "callback_data": f"question {price}"}] 
            for price in questions
        ]
    }


def create_answers_kb(answer: Answer) -> dict:
    return {
        "inline_keyboard": [
            [{
                "text": option,
                "callback_data": f"answer:{answer.question_id}:{idx}"
            }]
            for idx, option in enumerate(answer.answers.keys(), 1)
        ]
    }


def create_statistik_kb(chat_id: int) -> dict:
    return {
        "inline_keyboard": [
            [{
            "text": "Посмотреть статистику",
            "callback_data": f"stat_check chad_id: {chat_id}"
            }]
        ]
    } 