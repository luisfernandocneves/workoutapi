from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from centro_treinamento.models import CentroTreinamentoModel
from centro_treinamento.shcemas import CentroTreinamentoIn, CentroTreinamentoOut
from contrib.dependencies import DatabaseDependency


router = APIRouter()


@router.post(
    path="/",
    summary="Criar novo centro de treinamento",
    status_code=status.HTTP_201_CREATED,
    response_model=CentroTreinamentoOut,
)
async def post(
    db_session: DatabaseDependency, centrotreinamento_in: CentroTreinamentoIn = Body(...)
) -> CentroTreinamentoOut:
    try:
        centrotreinamento_out = CentroTreinamentoOut(id=uuid4(), **centrotreinamento_in.model_dump())
        centrotreinamento_model = CentroTreinamentoModel(**centrotreinamento_out.model_dump())
        db_session.add(centrotreinamento_model)
        await db_session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f'Já existe um centro de treinamento cadastrado com o nome: {centrotreinamento_in.nome}'
        )

    return centrotreinamento_out


@router.get(
    path="/",
    summary="Consultar todos os centros de treinamento",
    status_code=status.HTTP_200_OK,
    response_model=list[CentroTreinamentoOut],
)
async def query(db_session: DatabaseDependency) -> list[CentroTreinamentoOut]:
    centros_treinamento: list[CentroTreinamentoOut] = (
        (await db_session.execute(select(CentroTreinamentoModel))).scalars().all()
    )
    return centros_treinamento


@router.get(
    path="/{id}",
    summary="Consultar centro de treinamento por id",
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
)
async def query(id: UUID4, db_session: DatabaseDependency) -> CentroTreinamentoOut:
    centro_treinamento: CentroTreinamentoOut = (
        (await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Centro de treinamento não encontrado para o id: {id}",
        )
    else:
        return centro_treinamento
