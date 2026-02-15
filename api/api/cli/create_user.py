from itertools import count
import re

import click
from sqlmodel import select

from api.models import AsyncSession, User, UserRole
from api.auth import create_password, create_hash_salt


async def _create_user(email, fullname, username, password, is_admin):
    role = UserRole.ADMIN if is_admin else UserRole.STUDENT
    if not password:
        password = create_password()
    async with AsyncSession() as session:
        if not username:
            username = re.sub(r"[^a-z. ]+", "", fullname.strip().lower())
            username = re.sub(r"\s+", ".", username.strip())
            users = await session.exec(
                select(User.username).where(User.username.like(username + "%"))
            )
            usernames = users.all()
            next_username = username
            counter = count()
            while next_username in usernames:
                next_username = username + str(next(counter))
            username = next_username
        print(username)
        phash, salt = create_hash_salt(password)
        user = User(
            username=username,
            email=email,
            fullname=fullname,
            password_hash=phash,
            password_salt=salt,
            is_admin=is_admin,
            role=role,
        )
        session.add(user)
        await session.commit()
    click.echo(f"User ID {user.id}. Username: {user.username}. Password: {password}")
