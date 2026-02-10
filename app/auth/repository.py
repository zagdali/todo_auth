# app/auth/repository.py
from datetime import datetime
from sqlmodel import Session, select, update
from uuid import UUID, uuid4

from app.models.user import User, Tokens


class AuthRepository:

    def get_user_by_email(self, session: Session, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return session.exec(stmt).first()

    def create_user(self, session: Session, user: User):
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    # refresh tokens

    def save_refresh_token(self, session: Session, token: Tokens):
        session.add(token)
        session.commit()

    def get_refresh_token(self, session: Session, token_hash: str) -> Tokens | None:
        stmt = select(Tokens).where(
            Tokens.token_hash == token_hash,
            Tokens.revoked_at.is_(None),
            Tokens.expires_at > datetime.utcnow(),
        )
        return session.exec(stmt).first()

    def revoke_refresh_token(self, session: Session, token: Tokens): # отзыв токена
        token.revoked_at = datetime.utcnow()
        session.add(token)
        session.commit()


# отзыв всех токенов
    def revoke_all_refresh_tokens(
            self,
            session: Session,
            user_id,
    ) -> None:
        stmt = (
            update(Tokens)
            .where(
                Tokens.user_id == user_id,
                Tokens.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.utcnow())
        )

        session.exec(stmt)
        session.commit()

# email confirmation tokens
    def create_token(
                    self,
                    session: Session,
                    user_id: UUID,
                    token_type: str,
                    expires_at: datetime
                    ) -> Tokens:
        token_str = str(uuid4())
        token = Tokens(
            user_id=user_id,
            token=token_str,
            token_type=token_type,
            expires_at=expires_at
        )
        session.add(token)
        session.commit()
        session.refresh(token)
        return token

    # email validation tokens
    def get_valid_token(
                        self,
                        session: Session,
                        token: str,
                        token_type: str
                        ) -> Tokens | None:
        stmt = select(Tokens).where(
            Tokens.token == token,
            Tokens.token_type == token_type,
            Tokens.is_used == False,
            Tokens.expires_at > datetime.utcnow()
        )
        return session.exec(stmt).first()

    def update_token(self, session: Session, token: Tokens):
        session.add(token)
        session.commit()
        session.refresh(token)