from fastapi import APIRouter, responses

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import database.channels as channels
import utilities.generation as generation

router = APIRouter(prefix="/channels")

@router.post("/channels")
async def channels(parameters: None):
    pass