from datetime import datetime, timedelta

from sqlalchemy import Engine
from sqlmodel import create_engine, Session, select, between

from infra.chroma_store import is_in_vectorstore, \
    connect_to_chroma_collection, update_collection_with_patch
from infra.redis_queue import get_redis_queue, MAX_JOB_TIMEOUT, get_job
from scheme.nomenclature_scheme import SyncNomenclaturesPatch, MsuDatabaseOneNomenclatureRead, JobIdRead, \
    SyncOneNomenclature


def fetch_nomenclatures(engine: Engine, sync_period: int) -> list[MsuDatabaseOneNomenclatureRead]:
    with Session(engine) as session:
        st = select(MsuDatabaseOneNomenclatureRead) \
            .where(MsuDatabaseOneNomenclatureRead.is_group == 0) \
            .where(
            between(
                expr=MsuDatabaseOneNomenclatureRead.edited_at,
                lower_bound=datetime.now() - timedelta(hours=sync_period),
                upper_bound=datetime.now()
            ))
        result = session.exec(st).all()
        print(f"noms: {result}")

    return list(result)


def get_root_group_name(engine: Engine, parent: str):
    with Session(engine) as session:
        current_parent = parent
        root_group: MsuDatabaseOneNomenclatureRead
        while current_parent != "00000000-0000-0000-0000-000000000000":
            st = select(MsuDatabaseOneNomenclatureRead) \
                .where(MsuDatabaseOneNomenclatureRead.id == current_parent)
            root_group = session.exec(st).first()
            current_parent = str(root_group.group)

    root_group_name = root_group.nomenclature_name
    return root_group_name


def get_chroma_patch_for_sync(nomenclatures: list[MsuDatabaseOneNomenclatureRead]) -> list[SyncNomenclaturesPatch]:
    patch_for_chroma: list[SyncNomenclaturesPatch] = []
    for nom in nomenclatures:
        sync_nom = SyncOneNomenclature(
            id=str(nom.id),
            nomenclature_name=str(nom.nomenclature_name),
            group=str(nom.group)
        )

        if not nom.is_in_vectorstore:
            if str(nom.root_group_name) == "0001 Новая структура справочника" and not nom.is_deleted:
                patch_for_chroma.append(
                    SyncNomenclaturesPatch(
                        nomenclature_data=sync_nom,
                        action="create"
                    )
                )
            continue

        if str(nom.root_group_name) != "0001 Новая структура справочника" or nom.is_deleted:
            patch_for_chroma.append(
                SyncNomenclaturesPatch(
                    nomenclature_data=sync_nom,
                    action="delete"
                )
            )
            continue

        patch_for_chroma.append(
            SyncNomenclaturesPatch(
                nomenclature_data=sync_nom,
                action="update"
            )
        )

    return patch_for_chroma


def synchronize_nomenclatures(
    nom_db_con_str: str,
    chroma_collection_name: str,
    sync_period: int,
):
    engine = create_engine(nom_db_con_str)
    nomenclatures: list[MsuDatabaseOneNomenclatureRead] = fetch_nomenclatures(engine, sync_period)
    for nom in nomenclatures:
        nom.root_group_name = get_root_group_name(engine, str(nom.group))

    collection = connect_to_chroma_collection(chroma_collection_name)
    for nom in nomenclatures:
        nom.is_in_vectorstore = is_in_vectorstore(collection=collection, ids=str(nom.id))

    chroma_patch = get_chroma_patch_for_sync(nomenclatures)
    print(f"chroma patch: {chroma_patch}")
    return update_collection_with_patch(collection, chroma_patch)


def start_synchronizing_nomenclatures(
    nom_db_con_str: str,
    chroma_collection_name: str,
    sync_period: int,
):
    queue = get_redis_queue()
    job = queue.enqueue(
        synchronize_nomenclatures,
        nom_db_con_str,
        chroma_collection_name,
        sync_period,
        result_ttl=-1,
        job_timeout=MAX_JOB_TIMEOUT,
    )
    return JobIdRead(job_id=job.id)


def get_sync_nomenclatures_job_result(job_id: str):
    job = get_job(job_id)
    print(f"job: {job}")
    print(f"result: {job.result}")

    if job.result is None:
        return {"status": "syncing"}

    return job.result
