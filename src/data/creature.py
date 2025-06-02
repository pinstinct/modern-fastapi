from data.init import curs, IntegrityError
from error import Missing, Duplicate
from model.creature import Creature

curs.execute(
    """
    create table if not exists creature(
        name text primary key,
        description text,
        country text,
        area text,
        aka text
    )
"""
)


def row_to_model(row: tuple) -> Creature:
    """fetch 함수가 반환한 튜플을 모델 객체로 변환한다."""
    name, description, country, area, aka = row
    return Creature(
        name=name,
        description=description,
        country=country,
        area=area,
        aka=aka,
    )


def model_to_dict(creature: Creature) -> dict:
    """Ptdantic 모델을 딕셔너리로 변환해 'named' 쿼리 매개변수로 알맞게 지정한다."""
    return creature.model_dump()


def get_one(name: str) -> Creature:
    qry = "select * from creature where name = :name"
    params = {"name": name}
    curs.execute(qry, params)
    row = curs.fetchone()
    if row:
        return row_to_model(row)
    else:
        raise Missing(msg=f"Creature {name} not found")


def get_all() -> list[Creature]:
    qry = "select * from creature"
    curs.execute(qry)
    rows = list(curs.fetchall())
    return [row_to_model(row) for row in rows]


def create(creature: Creature) -> Creature:
    if not creature:
        return None
    qry = """insert into creature values (:name, :description, :country, :area, :aka)"""
    params = model_to_dict(creature)
    try:
        curs.execute(qry, params)
    except IntegrityError:
        raise Duplicate(msg=f"Creature {creature.name} already exists")
    return get_one(creature.name)


def modify(name: str, creature: Creature) -> Creature:
    qry = """update creature
        set country = :country, 
            name = :name,
            description = :description,
            area = :area,
            aka = :aka
        where name = :name_orig
    """
    params = model_to_dict(creature)
    params["name_orig"] = creature.name
    curs.execute(qry, params)
    if curs.rowcount == 1:
        return get_one(creature.name)
    else:
        raise Missing(msg=f"Creature {name} not found")


def replace(creature: Creature):
    return creature


def delete(name: str):
    if not name:
        return False
    qry = "delete from creature where name = :name"
    params = {"name": name}
    curs.execute(qry, params)
    if curs.rowcount != 1:
        raise Missing(msg=f"Creature {name} not found")
