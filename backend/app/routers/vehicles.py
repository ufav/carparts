from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.vehicle import VehicleMake, VehicleModel


router = APIRouter(tags=["vehicles"]) 


@router.get("/vehicles/makes", response_model=list[str])
def get_makes(db: Session = Depends(get_db)):
    rows = db.query(VehicleMake).filter(VehicleMake.is_active == True).order_by(VehicleMake.name).all()
    return [r.name for r in rows]


@router.get("/vehicles/models", response_model=list[str])
def get_models(make: str = Query(...), db: Session = Depends(get_db)):
    make_row = db.query(VehicleMake).filter((VehicleMake.slug == make) | (VehicleMake.name == make)).first()
    if not make_row:
        return []
    rows = (
        db.query(VehicleModel)
        .filter(VehicleModel.make_id == make_row.id, VehicleModel.is_active == True)
        .order_by(VehicleModel.name)
        .all()
    )
    return [r.name for r in rows]


@router.get("/vehicles/years", response_model=list[int])
def get_years(make: str = Query(...), model: str = Query(...), db: Session = Depends(get_db)):
    make_row = db.query(VehicleMake).filter((VehicleMake.slug == make) | (VehicleMake.name == make)).first()
    if not make_row:
        return []
    model_row = (
        db.query(VehicleModel)
        .filter(
            VehicleModel.make_id == make_row.id,
            (VehicleModel.slug == model) | (VehicleModel.name == model),
            VehicleModel.is_active == True,
        )
        .first()
    )
    if not model_row:
        return []
    y_from = model_row.year_from or 1900
    y_to = model_row.year_to or y_from
    return list(range(y_from, y_to + 1))


@router.get("/vehicles/submodels", response_model=list[str])
def get_submodels(
    make: str = Query(...),
    model: str = Query(...),
    year: int = Query(...),
    db: Session = Depends(get_db),
):
    # Если в БД нет детализации — вернём дефолтный набор
    return ["Base", "Sport", "Limited"]


@router.get("/vehicles/variants", response_model=list[str])
def get_variants(
    make: str = Query(...),
    model: str = Query(...),
    year: int = Query(...),
    submodel: str = Query(...),
    db: Session = Depends(get_db),
):
    return ["FWD", "AWD"]


@router.get("/vehicles/engines", response_model=list[str])
def get_engines(
    make: str = Query(...),
    model: str = Query(...),
    year: int = Query(...),
    submodel: str = Query(...),
    variant: str = Query(...),
    db: Session = Depends(get_db),
):
    # Возвращаем строки двигателей; фронт использует их для IVehicle.engine
    return ["1.6L", "2.0L", "2.5L"]


