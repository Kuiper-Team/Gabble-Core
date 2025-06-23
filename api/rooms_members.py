from fastapi import APIRouter, responses

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import database.rooms as rooms
import utilities.generation as generation

router = APIRouter(prefix="/rooms/members")

@router.post("/rooms/members")
async def rooms_members(parameters=None):
    pass

@router.post("/rooms/members/kick")
async def rooms_members_kick(parameters=None):
    pass

@router.post("/rooms/members/ban")
async def rooms_members_ban(parameters=None):
    pass