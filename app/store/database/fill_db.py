from app.store.database.modles import ThemeModel, QuestionModel, AnswerModel
from app.base.base_accessor import BaseAccessor
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select 


theme_data = [
    {"theme_name": "История"},
    {"theme_name": "География"},
    {"theme_name": "Наука"},
    {"theme_name": "Спорт"},
    {"theme_name": "Кино"}
]

question_data = [
    # История
    {"theme_id": 1, "price": 100, "question_text": "В каком году произошла Октябрьская революция?"},
    {"theme_id": 1, "price": 200, "question_text": "Как называлась первая мировая война?"},
    {"theme_id": 1, "price": 300, "question_text": "Кто был первым президентом США?"},
    {"theme_id": 1, "price": 100, "question_text": "В каком году пала Берлинская стена?"},
    {"theme_id": 1, "price": 200, "question_text": "Кто написал 'Капитал'?"},
    {"theme_id": 1, "price": 300, "question_text": "В каком году началась Великая Отечественная война?"},

    # География
    {"theme_id": 2, "price": 100, "question_text": "Какой самый большой океан в мире?"},
    {"theme_id": 2, "price": 200, "question_text": "Сколько материков существует?"},
    {"theme_id": 2, "price": 300, "question_text": "Как называется самая высокая гора в мире?"},
    {"theme_id": 2, "price": 100, "question_text": "Какой город называют 'Вечным'?"},
    {"theme_id": 2, "price": 200, "question_text": "Какое самое глубокое озеро в мире?"},
    {"theme_id": 2, "price": 300, "question_text": "Как называется самая длинная река в мире?"},

    # Наука
    {"theme_id": 3, "price": 100, "question_text": "Какой элемент имеет символ O?"},
    {"theme_id": 3, "price": 200, "question_text": "Кто открыл закон всемирного тяготения?"},
    {"theme_id": 3, "price": 300, "question_text": "Как называется наука о живых организмах?"},
    {"theme_id": 3, "price": 100, "question_text": "Сколько хромосом у человека?"},
    {"theme_id": 3, "price": 200, "question_text": "Что измеряется в амперах?"},
    {"theme_id": 3, "price": 300, "question_text": "Как называется процесс превращения жидкости в пар?"},

    # Спорт
    {"theme_id": 4, "price": 100, "question_text": "Сколько игроков в команде по футболу?"},
    {"theme_id": 4, "price": 200, "question_text": "Кто известен как 'Король футбола'?"},
    {"theme_id": 4, "price": 300, "question_text": "Какой мяч используется в гольфе?"},
    {"theme_id": 4, "price": 100, "question_text": "Сколько сетов может быть в теннисном матче?"},
    {"theme_id": 4, "price": 200, "question_text": "Как называется удар ногой в боксе?"},
    {"theme_id": 4, "price": 300, "question_text": "Сколько метров в марафонской дистанции?"},

    # Кино
    {"theme_id": 5, "price": 100, "question_text": "Какого цвета был конь у Росомахи?"},
    {"theme_id": 5, "price": 200, "question_text": "Кто сказал: 'Я вернусь'?"},
    {"theme_id": 5, "price": 300, "question_text": "Как называется фильм с динозаврами Стивена Спилберга?"},
    {"theme_id": 5, "price": 100, "question_text": "Какое прозвище у героя Леонардо ДиКаприо в 'Волке с Уолл-стрит'?"},
    {"theme_id": 5, "price": 200, "question_text": "Как называется фильм про космическую станцию с Джорджем Клуни?"},
    {"theme_id": 5, "price": 300, "question_text": "Как называется фильм, где главный герой застрял на необитаемом острове?"}
]

answer_data = [
    # История
    {"question_id": 1, "answers": {"1917": True, "1918": False, "1919": False, "1920": False}},
    {"question_id": 2, "answers": {"Первая мировая война": True, "Вторая мировая война": False, "Третья мировая война": False, "Четвертая мировая война": False}},
    {"question_id": 3, "answers": {"Джордж Вашингтон": True, "Бенjamin Franklin": False, "Абрахам Линкольн": False, "Томас Эдисон": False}},
    {"question_id": 4, "answers": {"1989": True, "1988": False, "1990": False, "1991": False}},
    {"question_id": 5, "answers": {"Карл Маркс": True, "Фридрих Энгельс": False, "Владимир Ленин": False, "Иосиф Сталин": False}},
    {"question_id": 6, "answers": {"1941": True, "1939": False, "1945": False, "1950": False}},

    # География
    {"question_id": 7, "answers": {"Тихий океан": True, "Атлантический океан": False, "Индийский океан": False, "Северный Ледовитый океан": False}},
    {"question_id": 8, "answers": {"7": True, "5": False, "6": False, "8": False}},
    {"question_id": 9, "answers": {"Эверест": True, "Килиманджаро": False, "Макалу": False, "Эльбрус": False}},
    {"question_id": 10, "answers": {"Рим": True, "Париж": False, "Лондон": False, "Берлин": False}},
    {"question_id": 11, "answers": {"Байкал": True, "Виктория": False, "Титикака": False, "Супеси": False}},
    {"question_id": 12, "answers": {"Нил": True, "Амазонка": False, "Янцзы": False, "Миссисипи": False}},

    # Наука
    {"question_id": 13, "answers": {"Кислород": True, "Азот": False, "Углерод": False, "Водород": False}},
    {"question_id": 14, "answers": {"Исаак Ньютон": True, "Альберт Эйнштейн": False, "Никола Тесла": False, "Галилео Галилей": False}},
    {"question_id": 15, "answers": {"Биология": True, "Физика": False, "Химия": False, "Геология": False}},
    {"question_id": 16, "answers": {"46": True, "23": False, "69": False, "92": False}},
    {"question_id": 17, "answers": {"Ток": True, "Напряжение": False, "Сопротивление": False, "Энергия": False}},
    {"question_id": 18, "answers": {"Испарение": True, "Конденсация": False, "Оттаивание": False, "Замерзание": False}},

    # Спорт
    {"question_id": 19, "answers": {"11": True, "10": False, "12": False, "13": False}},
    {"question_id": 20, "answers": {"Пеле": True, "Месси": False, "Роналду": False, "Марадона": False}},
    {"question_id": 21, "answers": {"Гольф-мяч": True, "Теннисный мяч": False, "Баскетбольный мяч": False, "Футбольный мяч": False}},
    {"question_id": 22, "answers": {"3 или 5": True, "2 или 4": False, "1 или 3": False, "4 или 6": False}},
    {"question_id": 23, "answers": {"Кик": True, "Панч": False, "Хук": False, "Апперкот": False}},
    {"question_id": 24, "answers": {"42,195": True, "26,2": False, "50": False, "100": False}},

    # Кино
    {"question_id": 25, "answers": {"Белый": True, "Черный": False, "Красный": False, "Синий": False}},
    {"question_id": 26, "answers": {"Терминатор": True, "Рокки": False, "Рэмбо": False, "Бэтмен": False}},
    {"question_id": 27, "answers": {"Парк Юрского периода": True, "Динозавры": False, "Мир динозавров": False, "Затерянный мир": False}},
    {"question_id": 28, "answers": {"Жорж": True, "Волк": False, "Джордан": False, "Лео": False}},
    {"question_id": 29, "answers": {"Гравитация": True, "Космос": False, "Стар": False, "Небо": False}},
    {"question_id": 30, "answers": {"Похищенные": True, "Остаться в живых": False, "Пустыня": False, "Остров": False}}
]

class DbaseAccessor(BaseAccessor):
    async def add_themes(self, theme_data: list[dict]) -> bool:
        async with self.app.database.session() as session:
            try:
                for theme in theme_data:
                    stmt = (
                        insert(ThemeModel)
                        .values(theme_name=theme["theme_name"])
                        .on_conflict_do_nothing(index_elements=["theme_name"])
                    )
                    await session.execute(stmt)
                await session.commit()
                self.logger.info("Темы успешно добавлены.")
                return True
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Ошибка при добавлении тем: {e}")
                return False

    async def add_questions(self, question_data: list[dict]) -> dict[int, int] | None:
        async with self.app.database.session() as session:
            try:
                # Получаем все существующие темы
                result = await session.execute(select(ThemeModel._id))
                existing_theme_ids = {t[0] for t in result.all()}
                
                id_mapping = {}
                
                for question in question_data:
                    if question["theme_id"] not in existing_theme_ids:
                        self.logger.warning(f"Тема с ID {question['theme_id']} не найдена. Вопрос пропущен.")
                        continue

                    stmt = (
                        insert(QuestionModel)
                        .values(
                            theme_id=question["theme_id"],
                            price=question["price"],
                            question_text=question["question_text"],
                        )
                        .returning(QuestionModel.question_id)
                    )
                    
                    result = await session.execute(stmt)
                    question_id = result.scalar_one_or_none()
                    
                    if question_id:
                        original_id = question_data.index(question) + 1
                        id_mapping[original_id] = question_id

                await session.commit()
                self.logger.info(f"Добавлено {len(id_mapping)} вопросов.")
                return id_mapping
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Ошибка при добавлении вопросов: {e}")
                return None

    async def add_answers(self, answer_data: list[dict], question_mapping: dict[int, int]) -> bool:
        async with self.app.database.session() as session:
            try:
                added_count = 0
                
                for answer in answer_data:
                    real_question_id = question_mapping.get(answer["question_id"])
                    if not real_question_id:
                        continue

                    # Формируем ответы в строгом формате [{"текст": bool}]
                    formatted_answers = [{k: v} for k, v in answer["answers"].items()]

                    stmt = (
                        insert(AnswerModel)
                        .values(
                            question_id=real_question_id,
                            answers=formatted_answers
                        )
                        .on_conflict_do_nothing(index_elements=["question_id"])
                    )
                    await session.execute(stmt)
                    added_count += 1

                await session.commit()
                self.logger.info(f"Успешно добавлено {added_count} ответов.")
                return True
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Ошибка при добавлении ответов: {e}")
                return False

    async def populate_database(self) -> bool:
        try:
            # 1. Добавляем темы
            if not await self.add_themes(theme_data):
                return False
            
            # 2. Добавляем вопросы и получаем маппинг ID
            question_mapping = await self.add_questions(question_data)
            if not question_mapping:
                return False
            
            # 3. Добавляем ответы с учетом реальных ID вопросов
            if not await self.add_answers(answer_data, question_mapping):
                return False
                
            self.logger.info("База данных успешно заполнена.")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при заполнении базы данных: {e}")
            return False