from fastapi import APIRouter, Depends

import api.controls as controls
import api.data_models as data_models
import database.invites as invites
import api.presets as presets
import database.sqlite_wrapper as sql

router = APIRouter()

@router.post("/invites")
async def r_invites(parameters: data_models.Invite, token: str = Depends(controls.oauth2_scheme)):
    if not invites.exists(parameters.uuid): return presets.noinvite
    if not invites.verify_passcode(parameters.uuid): return presets.incorrectpasscode

    try:
        data = sql.select(invites.table, "uuid", parameters.uuid, exception="noinvite")
    except Exception as code:
        return presets.auto(code)

    return {
        "success": True,
        "data": {
            "uuid": parameters.uuid,
            "action": invites.get_action(parameters.uuid, parameters.passcode),
            "expiry": data[2]
        },
    }

@router.post("/invites/accept")
async def invites_accept(parameters: data_models.InviteAccept, token: str = Depends(controls.oauth2_scheme)):
    if not invites.exists(parameters.uuid): return presets.noinvite
    if not invites.verify_passcode(parameters.uuid): return presets.incorrectpasscode

    access_token = await controls.authenticate(token)
    try:
        invites.accept(access_token[1], parameters.uuid, parameters.passcode)
    except Exception as code:
        presets.auto(code)

    return presets.success

@router.post("/invites/create")
async def invites_create(parameters: data_models.InviteCreate, token: str = Depends(controls.oauth2_scheme)):
    if invites.exists(parameters.uuid): return presets.alreadyexists

    def invite_parameters(model):
        return model(**dict(zip(model.model_fields.keys(), parameters.invite_parameters)))
    if parameters.type == 0:
        if not controls.verify_model(invite_parameters(data_models.InviteParameters0), data_models.InviteParameters0): return presets.invalidformat
    elif parameters.type == 1:
        if not controls.verify_model(invite_parameters(data_models.InviteParameters1), data_models.InviteParameters1): return presets.invalidformat

    try:
        invites.create()
    except Exception as code:
        presets.auto(code)

    return presets.success