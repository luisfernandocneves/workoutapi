from datetime import datetime
from typing import Union
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from sqlalchemy.future import select
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from atleta.models import AtletaModel
from atleta.schemas import AtletaGetAll, AtletaIn, AtletaOut, AtletaUpdate
from categorias.models import CategoriasModel
from centro_treinamento.models import CentroTreinamentoModel
from contrib.dependencies import DatabaseDependency

router = APIRouter()


@router.post(
    path="/",
    summary="Criar novo atleta",
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut,
)
async def post(
    db_session: DatabaseDependency, atleta_in: AtletaIn = Body(...)
) -> AtletaOut:
    categoria = (
        (
            await db_session.execute(
                select(CategoriasModel).filter_by(nome=atleta_in.categoria.nome)
            )
        )
        .scalars()
        .first()
    )
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'A categoria {atleta_in.categoria.nome} não foi encontrada.'
        )
    centro_treinamento = (
        (
            await db_session.execute(
                select(CentroTreinamentoModel).filter_by(nome=atleta_in.centro_treinamento.nome)
            )
        )
        .scalars()
        .first()
    )
    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'O Centro de Treinamento {atleta_in.centro_treinamento.nome} não foi encontrado.'
        )
    atleta_out = AtletaOut(
        id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump()
    )
    try:
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id
        db_session.add(atleta_model)
        await db_session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f'Já existe um atleta cadastrado com o cpf: {atleta_in.cpf}'
        )

    return atleta_out

@router.get(
    path="/",
    summary="Consultar todos os atletas",
    status_code=status.HTTP_200_OK,
    response_model=list[AtletaGetAll],
)
async def query(nome: Union[str, None] = '', cpf: Union[str, None] = '', db_session: DatabaseDependency = None) -> list[AtletaGetAll]:
    if nome or cpf:
        
        atletas: list[AtletaGetAll] = (
            (await db_session.execute(select(AtletaModel).where(or_(AtletaModel.nome.like(nome), AtletaModel.cpf == cpf)))).scalars().all()
        )    
    
    else:
        atletas: list[AtletaGetAll] = (
            (await db_session.execute(select(AtletaModel.nome, AtletaModel.centro_treinamento, AtletaModel.categoria))).scalars().all()
        )        

    if not atletas:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atletas não encontrados para a condição informada.",
        )
    else:
        atleta_up = atletas.model_dump(exclude_unset=True)
        for key, value in atleta_up.items():
            setattr(atletas, key, value)
        return atletas

@router.get(
    path="/{id}",
    summary="Consultar atleta por id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def query(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado para o id: {id}",
        )
    else:
        return atleta


@router.patch(
    path="/{id}",
    summary="Editar um atleta por id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def patch(id: UUID4, db_session: DatabaseDependency, atleta_update: AtletaUpdate = Body(...)) -> AtletaOut:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado para o id: {id}",
        )
    else:
        atleta_up = atleta_update.model_dump(exclude_unset=True)
        for key, value in atleta_up.items():
            setattr(atleta, key, value)
        await db_session.commit()
        await db_session.refresh(atleta)
        return atleta

@router.delete(
    path="/{id}",
    summary="Excluir um atleta por id",
    status_code=status.HTTP_204_NO_CONTENT
)
async def query(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrado para o id: {id}",
        )
    else:
        await db_session.delete(atleta)
        await db_session.commit()