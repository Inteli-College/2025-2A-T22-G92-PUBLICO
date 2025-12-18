import os
from datetime import datetime, timedelta
from typing import Union, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

# Configurações do Ambiente
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key_insegura")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# Banco de Dados Simulado de Usuários Para Teste
# role: 'admin' pode ver tudo, os demais têm restrições
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrador do Sistema",
        "email": "admin@inteli.edu.br",
        "hashed_password": "$2b$12$4qBuQROiwA0tecZ7mSmUhOtLTfU8dgkX7bQGGIHh7frRMPPJ0hz7O", # Senha: admin
        "disabled": False,
        "role": "admin"
    },
    "aluno": {
        "username": "aluno",
        "full_name": "Aluno Inteli",
        "email": "aluno@inteli.edu.br",
        "hashed_password": "$2b$12$4qBuQROiwA0tecZ7mSmUhOtLTfU8dgkX7bQGGIHh7frRMPPJ0hz7O", # Senha: admin
        "disabled": False,
        "role": "aluno"
    },
    "gerente": {
        "username": "gerente",
        "full_name": "Gerente BOFA",
        "email": "gerente@bofa.com.br",
        "hashed_password": "$2b$12$4qBuQROiwA0tecZ7mSmUhOtLTfU8dgkX7bQGGIHh7frRMPPJ0hz7O", # Senha: admin
        "disabled": False,
        "role": "gerente"
    },
    "analista": {
        "username": "analista",
        "full_name": "Analista BOFA",
        "email": "analista@bofa.com.br",
        "hashed_password": "$2b$12$4qBuQROiwA0tecZ7mSmUhOtLTfU8dgkX7bQGGIHh7frRMPPJ0hz7O", # Senha: admin
        "disabled": False,
        "role": "analista"
    }
}

# Modelos Pydantic
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None
    role: Union[str, None] = None

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
    role: str

class UserInDB(User):
    hashed_password: str

# Utilitários de Segurança
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependência para Proteger Rotas
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception
    
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    return current_user