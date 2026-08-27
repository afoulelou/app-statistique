from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.models import User


def test_users_schema_can_be_created_on_sqlite() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    assert "users" in inspect(engine).get_table_names()

    with Session(engine) as session:
        user = User(
            first_name="Awa",
            last_name="Diallo",
            email="awa@example.com",
            password_hash="not-a-real-password-hash",
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        assert user.id is not None
        assert user.email == "awa@example.com"
