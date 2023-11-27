import os

from fastapi import APIRouter, Depends
from fastapi_versioning import version
from redis import Redis
from rq.job import Job
from rq.command import send_stop_job_command
from rq.registry import StartedJobRegistry
from rq.queue import Queue

from dto.file_upload_task_dto import FileUploadTaskDto
from model import file_model
from repository import file_repository
from dto.user_dto import UserDto
from service.auth_service import AuthService

router = APIRouter(
    prefix="/task",
    tags=["task"],
)


def get_current_user_job(user_id: str) -> Job | None:
    redis = Redis(host=os.getenv("REDIS_HOST", "local"))
    q = Queue("document", connection=redis)
    registry = StartedJobRegistry(name="document", connection=redis)
    job_ids: list = registry.get_job_ids()
    job_ids.extend(q.get_job_ids())
    all_jobs = Job.fetch_many(job_ids, connection=redis)
    for job in all_jobs:
        if job.get_meta(refresh=True).get("user_id", None) == user_id:
            return job
    return None


@router.get("/file_upload/active", response_model=list[FileUploadTaskDto])
@version(1)
def get_active_file_upload_tasks(current_user: UserDto = Depends(AuthService.get_current_user)):
    current_user_job = get_current_user_job(current_user.id)
    if not current_user_job:
        return []

    if current_user_job.get_status(refresh=True) in ["finished", "failed", "stopped"]:
        return []

    return [FileUploadTaskDto(
        id=current_user_job.id,
        status=current_user_job.get_status(refresh=True),
        progress=current_user_job.get_meta(refresh=True).get("progress", None),
        full_work=current_user_job.get_meta(refresh=True).get("full_work", None)
    )]


@router.delete("/file_upload/{task_id}", response_model=FileUploadTaskDto)
@version(1)
def interrupt_task_by_id(current_user: UserDto = Depends(AuthService.get_current_user)):
    redis = Redis(host=os.getenv("REDIS_HOST", "localhost"))
    current_user_job = get_current_user_job(current_user.id)
    send_stop_job_command(redis, current_user_job.id)

    file = file_repository.get_file_by_id(current_user_job.get_meta(refresh=True)["file_id"])
    file_model.delete_file(file)

    return FileUploadTaskDto(
        id=current_user_job.id,
        status=current_user_job.get_status(refresh=True),
        progress=current_user_job.get_meta(refresh=True).get("progress", None),
        full_work=current_user_job.get_meta(refresh=True).get("full_work", None)
    )
