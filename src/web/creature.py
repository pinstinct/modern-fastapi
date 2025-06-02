from fastapi import APIRouter, HTTPException

from error import Missing, Duplicate
from model.creature import Creature
from service import creature as service

router = APIRouter(prefix="/creature")


@router.get("")
def get_all() -> list[Creature]:
    return service.get_all()


@router.get("/{name}")
def get_one(name) -> Creature:
    try:
        return service.get_one(name)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)


@router.post("", status_code=201)
def create(creature: Creature) -> Creature:
    try:
        return service.create(creature)
    except Duplicate as exc:
        raise HTTPException(status_code=404, detail=exc.msg)


@router.patch("/{name}")
def modify(name, creature: Creature) -> Creature:
    try:
        return service.modify(name, creature)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)


@router.patch("/{name}")
def replace(name, creature: Creature) -> Creature:
    try:
        return service.replace(name, creature)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)


@router.delete("/{name}")
def delete(name: str):
    try:
        return service.delete(name)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
