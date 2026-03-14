from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings
from app.core.security import tenant_context
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


async def get_current_user_context(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        user_id: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")

        if user_id is None or tenant_id is None:
            raise credentials_exception


        tenant_context.set(uuid.UUID(tenant_id))

        return {"user_id": user_id, "tenant_id": tenant_id}

    except (JWTError, ValueError):
        raise credentials_exception