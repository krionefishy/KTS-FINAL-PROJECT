from app.base.base_accessor import BaseAccessor
from app.store.database.modles import UserModel, User
from sqlalchemy import select

class UserAccessor(BaseAccessor):
    async def get_stats(self, user_id: int) -> User:
        async with self.app.database.session() as session:
            result = await session.execute(
                select(UserModel)
                .where(UserModel._id == user_id)
            )

            user = result.scalar_one_or_none()
            if user:
                return User(
                    id = user._id,
                    total_games=user.total_games,
                    total_wins=user.total_wins,
                    total_score=user.total_score
                )
            else:
                return User(
                    id = 0,
                    total_games=0,
                    total_wins=0,
                    total_score=0
                )
            

