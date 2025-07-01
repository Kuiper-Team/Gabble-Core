from fastapi import APIRouter, responses

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import database.messages as messages
import utilities.generation as generation

router = APIRouter()

@router.post("/messages")
async def r_messages(parameters: None):
    pass