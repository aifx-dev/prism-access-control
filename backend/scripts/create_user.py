import argparse
import asyncio
import os
import sys

from sqlalchemy import select

sys.path.insert(0, os.path.abspath(os.getcwd()))

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.models import User


async def _run(email: str, password: str, *, username: str, full_name: str | None, superuser: bool) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if user is None and email:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

        if user is None:
            user = User(
                username=username,
                email=email or None,
                hashed_password=get_password_hash(password),
                full_name=full_name,
                is_active=True,
                is_superuser=superuser,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print(f"OK created user username={user.username} email={user.email} superuser={user.is_superuser}")
            return

        user.email = email or user.email
        user.hashed_password = get_password_hash(password)
        user.full_name = full_name if full_name is not None else user.full_name
        user.is_active = True
        user.is_superuser = superuser
        await db.commit()
        print(f"OK updated user username={user.username} email={user.email} superuser={user.is_superuser}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create/update a Prism admin user.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--username", default=None, help="Login username (default: email).")
    parser.add_argument("--full-name", default="Administrator")
    parser.add_argument("--superuser", action="store_true", default=True)
    args = parser.parse_args()

    username = args.username or args.email
    asyncio.run(
        _run(
            email=args.email,
            password=args.password,
            username=username,
            full_name=args.full_name,
            superuser=bool(args.superuser),
        )
    )


if __name__ == "__main__":
    main()
