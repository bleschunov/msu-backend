from sqlmodel import Session
from scheme.prompt_scheme import PromptCreate, Prompt
from scheme.tenant_scheme import Tenant


# def get_prompt_by_tenant_id(session: Session, tenant_id: int) -> Prompt:
#     statement = select(Prompt).where(Prompt.tenant_id == tenant_id)
#     result = session.exec(statement)
#     prompt_db = result.one()
#     return prompt_db


def create_prompt(session: Session, prompt: PromptCreate) -> Prompt:
    tenant_db = session.get(Tenant, prompt.tenant_id)

    prompt_db = Prompt.from_orm(prompt)
    prompt_db.tenant = tenant_db

    session.add(prompt_db)
    session.commit()
    return prompt_db


# def update_prompt(session: Session, prompt_id: int, prompt: PromptUpdate) -> Prompt:
#     prompt_db = session.get(Prompt, prompt_id)
#
#     if prompt_db is None:
#         raise HTTPException(status_code=404, detail=f"Prompt with prompt_id={prompt_id} is not found.")
#
#     prompt_db.is_active = prompt.is_active
#     prompt_db.prompt = prompt.prompt
#     session.add(prompt_db)
#     session.commit()
#
#     return prompt_db
