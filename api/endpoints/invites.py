from fastapi import APIRouter, responses

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import database.invites as invites
import utilities.generation as generation

router = APIRouter(prefix="/invites")

@router.post("/invites")
async def invites(parameters: None):
    pass