from fastapi import APIRouter, responses

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import database.conversations as conversations
import utilities.generation as generation

router = APIRouter()

@router.post("/conversations")
async def r_conversations(parameters: None):
    pass