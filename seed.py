from app.core.database import SessionLocal
from app.modules.tenants.models import Tenant
from app.modules.users.models import User
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed():
    db = SessionLocal()
    t1 = Tenant(name="Banco Alpha", document="12345678000100")
    t2 = Tenant(name="Crédito Beta", document="98765432000199")
    db.add_all([t1, t2])
    db.commit()

    u1 = User(
        name="Admin Alpha",
        email="admin@alpha.com",
        password_hash=pwd_context.hash("123456"),
        tenant_id=t1.id,
        role="admin"
    )
    u2 = User(
        name="Operador Beta",
        email="user@beta.com",
        password_hash=pwd_context.hash("123456"),
        tenant_id=t2.id,
        role="operator"
    )
    db.add_all([u1, u2])
    db.commit()
    print("Seed finalizado com sucesso!")
    db.close()

if __name__ == "__main__":
    seed()