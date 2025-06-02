from sqlite3 import IntegrityError

from data.init import curs
from error import Missing, Duplicate
from model.user import PublicUser, PrivateUser

"""
user(활성 유저) 및 xuser(삭제된 유저) 테이블을 만든다.
개발자는 종종 유저 테이블에 불리언 deleted 필드를 추가해서, 실제로 테이블에서 레코드를 삭제하지 않고도 유저가 활동하지 않음을 나타낸다.
삭제된 유저의 테이터를 다른 테이블로 옮겨두면, 모든 유저 쿼리에서 삭제된 필드를 반복적으로 확인하지 않아도 된다.
그리고 쿼리 속도도 높아진다. (불리언과 같이 카디널리티가 낮은 필드에 대한 인덱스를 만드는 건 좋지 않다.)
"""

curs.execute(
    """
    create table if not exists user(
        name text primary key,
        hash text
    )
"""
)

curs.execute(
    """
    create table if not exists xuser(
        name text primary key,
        hash text
    )
"""
)


def row_to_model(row: tuple, is_public: bool = True) -> PublicUser | PrivateUser:
    """is_public 인자에 따라 나가는 모델이 분기된다."""
    name, hash = row
    if is_public:
        return PublicUser(name=name)
    else:
        return PrivateUser(name=name, hash=hash)


def model_to_dict(user: PrivateUser) -> dict:
    return user.model_dump()


def get_one(name: str, is_public: bool = True) -> PublicUser | PrivateUser:
    """유저 조회는 is_public에 따라 PublicUser 또는 PrivateUser를 반환한다."""
    qry = "select * from user where name = :name"
    params = {"name": name}
    curs.execute(qry, params)
    row = curs.fetchone()
    if row:
        return row_to_model(row, is_public=is_public)
    else:
        raise Missing(msg=f"User {name} not found")


def get_all() -> list[PublicUser]:
    """유저 목록 조회에서는 민감정보(hash)를 포함할 일이 없어 PublicUser 모델 집합을 반환한다."""
    qry = "select * from user"
    curs.execute(qry)
    return [row_to_model(row) for row in curs.fetchall()]


def create(user: PrivateUser, table: str = "user") -> PublicUser:
    """user 테이블 또는 xuser 테이블에 유저를 생성한다."""
    qry = f"""insert into {table} (name, hash) 
        values (:name, :hash)
    """
    params = model_to_dict(user)
    try:
        curs.execute(qry, params)
    except IntegrityError:
        raise Duplicate(msg=f"{table}: user {user.name} already exists")
    return PublicUser(name=user.name)


def modify(name: str, user: PublicUser) -> PublicUser:
    """name으로 조회한 유저의 이름을 수정한다."""
    qry = """
        update user 
        set name = :name
        where name = :name0
    """
    params = {"name": user.name, "name0": name}
    curs.execute(qry, params)
    if curs.rowcount == 1:
        return get_one(user.name)
    else:
        raise Missing(msg=f"User {name} not found")


def delete(name: str) -> None:
    """name으로 user 테이블에서 조회한 유저를 삭제하고, xuser 테이블에 추가한다."""
    user = get_one(name, is_public=False)
    qry = "delete from user where name = :name"
    params = {"name": name}
    curs.execute(qry, params)
    if curs.rowcount != 1:
        raise Missing(msg=f"User {name} not found")
    create(user, table="xuser")
