from fastapi import APIRouter, Depends
from fastapi_versioning import version

from dto.datastep_prediction_dto import DatastepPredictionOutDto
from dto.query_dto import QueryDto
from dto.user_dto import UserDto
from model.datastep_model import datastep_get_prediction
from service.auth_service import AuthService

router = APIRouter(
    prefix="/assistant",
    tags=["assistant"],
)


@router.post("/prediction", response_model=DatastepPredictionOutDto)
@version(1)
async def get_prediction(
    body: QueryDto,
    current_user: UserDto = Depends(AuthService.get_current_user),
):
    return await datastep_get_prediction(body, current_user.tenant_id, current_user.database_prediction_config)
