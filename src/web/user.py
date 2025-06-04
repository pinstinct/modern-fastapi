import os
from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from error import Missing, Duplicate
from model.user import PublicUser

if os.getenv("CRYPTID_UNIT_TEST"):
    from fake import user as service
else:
    from service import user as service

ACCESS_TOKEN_EXPIRE_MINUTES = 30


router = APIRouter(prefix="/user")


# --- 새로운 인증 관련 코드들

# 이 의존성은 "/user/token"을 동작하게 하고
# username과 pass를 담고 있는 form을 읽는다.
# 접근 토큰을 반환한다.
oauth2_dep = OAuth2PasswordBearer(tokenUrl="/user/token")


def unauthed():
    raise HTTPException(
        status_code=401,
        detail="Incorrect username or password",
        headers={"WWW-Authenticated": "Bearer"},
    )


@router.post("/token")
async def create_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """username과 password를 OAuth 양식에서 꺼내고 JWT 접근 토큰을 반환한다."""
    user = service.auth_user(form_data.username, form_data.password)
    if not user:
        unauthed()
    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = service.create_access_token(
        data={"sub": user.name},
        expires=expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


# 이 엔드포인트는 oauth2_dep() 의존성을 가지고 있다.
@router.get("/token")
def get_access_token(token: str = Depends(oauth2_dep)) -> dict:
    """현재 접근 토큰을 반환한다."""
    return {"token": token}


# --- 이전 CRUD 코드


@router.get("/")
def get_all() -> list[PublicUser]:
    return service.get_all()


@router.get("/{name}")
def get_one(name) -> PublicUser:
    try:
        return service.get_one(name)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
    except Duplicate as exc:
        raise HTTPException(status_code=409, detail=exc.msg)
