#Needs an overhaul
from datetime import datetime
from fastapi import APIRouter

import api.controls as controls
import api.data_models as data_models
import api.presets as presets
import database.invites as invites
import database.users as users
import utilities.cryptography as cryptography
import utilities.generation as generation
import utilities.validation as validation

router = APIRouter()

@router.post("/invites")
async def r_invites(parameters: data_models.Invite):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not controls.verify_passcode(parameters.uuid, parameters.passcode): return presets.incorrectpasscode

    try:
        data = controls.fetch_from_db("invite", "uuid", parameters.uuid)
    except Exception as code:
        return presets.auto(code)

    result = cryptography.aes_decrypt(data[3], parameters.passcode).split(",")
    if result[0] == "f":
        return {
            "success": True,
            "data": {
                "uuid": parameters.uuid,
                "type": result[0],
                "inviter": data[1],
                "invitee": result[2],
                "expiry": data[2]
            },
        }
    elif result[1] == "r":
        return {
            "success": True,
            "data": {
                "uuid": parameters.uuid,
                "type": result[0],
                "inviter": data[1],
                "invitee": result[2],
                "room_uuid": result[1],
                "expiry": data[2]
            }
        }

@router.post("/invites/accept")
async def invites_accept(parameters: data_models.InviteAccept):
    result = invites.get_result(parameters.uuid, parameters.passcode)

    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not controls.verify_passcode(parameters.uuid, parameters.passcode): return presets.incorrectpasscode
    if not validation.timestamp(controls.fetch_from_db("invites", "uuid", parameters.uuid, column="expiry")): return presets.inviteexpired

    if result[0] == "f":
        if not result[1] == parameters.hash_credentials.username: return presets.nopermission
        if not result[2] in users.friends(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.alreadyfriends
    elif result[0] == "r":
        if result[1] in users.key_chain(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.alreadyamember

    try:
        invites.accept(parameters.uuid, parameters.passcode, room_private_key=parameters.private_key)
    except Exception as code:
        return presets.auto(code)

@router.post("/invites/create") #If there are multiple targets, seperate usernames with comma.
async def invites_create(parameters: data_models.InviteCreate): #Will fetchone() cause a trouble here?
    f = parameters.type == "f" and parameters.target is None
    r = parameters.type == "r" and parameters.invalidformat is None
    if f or r: return presets.invalidformat
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not controls.verify_passcode(parameters.uuid, parameters.passcode): return presets.incorrectpasscode

    expiry_ts = generation.unix_timestamp(datetime.now()) + parameters.expiry
    try:
        if f: invites.create(parameters.hash_credentials.username, expiry_ts, "f,{},{}".format(parameters.hash_credentials.username, parameters.target), parameters.passcode)
        elif r: invites.create(parameters.hash_credentials.username, expiry_ts, "r,{},{}".format(parameters.room_uuid, parameters.hash_credentials.username), parameters.passcode)
    except Exception as code:
        return presets.auto(code)

@router.post("/invite/decline")
async def invite_decline(parameters: data_models.InviteDecline):
    f = parameters.type == "f"
    r = parameters.type == "r"
    if f or r: return presets.invalidformat
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash
    if not controls.verify_passcode(parameters.uuid, parameters.passcode): return presets.incorrectpasscode

    if f:
        try:
            invitees = invites.get_result(
                parameters.uuid,
                controls.fetch_from_db("invites", "uuid", parameters.uuid, column="inviter"),
                parameters.passcode
            ).split(",")
            del invitees[0]
            del invitees[1]
            if parameters.hash_credentials.username in invitees: return presets.notaninvitee
        except Exception as code:
            return presets.auto(code)

    try:
        invites.withdraw(parameters.uuid)
    except Exception as code:
        return presets.auto(code)

@router.post("/invite/withdraw")
async def invite_withdraw(parameters: data_models.Invite):
    if not controls.verify_hash(parameters.hash_credentials.username, parameters.hash_credentials.hash): return presets.incorrecthash

    try:
        inviter = controls.fetch_from_db("invites", "uuid", parameters.uuid, column="inviter")[0]
    except Exception as code:
        return presets.auto(code)
    else:
        if inviter == parameters.hash_credentials.username: return presets.nottheinviter

    try:
        invites.withdraw(parameters.uuid)
    except Exception as code:
        return presets.auto(code)