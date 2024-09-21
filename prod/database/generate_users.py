import asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from connect import async_session, init_db
from models import User

fake = Faker()

async def insert_random_users(db: AsyncSession, num_users: int = 100):
    """Insert random users into the database."""
    for _ in range(num_users):
        # Generate random user data
        nickname = fake.user_name()
        telegram_uid = str(fake.random_int(min=100000, max=999999))
        coins = fake.random_int(min=0, max=100)
        rating = fake.random_int(min=0, max=5)
        last_login = fake.date_time_this_year()
        last_logout = fake.date_time_this_year()

        # Create a new User object
        user = User(
            nickname=nickname,
            telegram_uid=telegram_uid,
            coins=coins,
            rating=rating,
            last_login=last_login,
            last_logout=last_logout,
        )

        # Add and commit the user to the database
        db.add(user)

    await db.commit()
    print(f"Inserted {num_users} random users into the database.")

async def main():
    # Initialize the database and session
    async with async_session() as session:
        await init_db()  # Initialize the database tables if not done already
        await insert_random_users(session, 100)

# Run the script
# if __name__ == "__main__":
#     asyncio.run(main())
