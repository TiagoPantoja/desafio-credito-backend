from sqlalchemy.orm import Session
from app.modules.users.models import User
from app.modules.tenants.models import Tenant
from app.core.security import verify_password, create_access_token
from fastapi import HTTPException, status


class AuthService:
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="E-mail ou senha incorretos"
            )

        if not user.is_active:
            raise HTTPException(status_code=400, detail="Usuário inativo")

        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()

        token_data = {
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "role": user.role
        }

        token = create_access_token(data=token_data)

        return {
            "access_token": token,
            "token_type": "bearer",
            "tenant_name": tenant.name
        }