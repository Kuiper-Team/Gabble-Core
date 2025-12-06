from pydantic import BaseModel, Field
from typing import Optional

ascii_r = r"^[\x00-\x7F]*$"
hash_hex_r = r"^[0-9a-fA-F]{32}$"
label_lengths = (3, 36)

argon2_hash_hex = Field(pattern=hash_hex_r)
body = Field(min_length=1, max_length=10000)
base64 = Field(min_length=1, pattern=r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$")
expiry = Field(ge=1, le=525600)
invite_type = Field(le=1)
label = Field(min_length=label_lengths[0], max_length=label_lengths[1], pattern=ascii_r) #ASCII
password = Field(min_length=12, max_length=72, pattern=ascii_r) #ASCII
private_key = Field(pattern=r"^-----BEGIN RSA PRIVATE KEY-----\s*.*\s*-----END RSA PRIVATE KEY-----$")
public_key = Field(pattern=r"/-----BEGIN RSA PUBLIC KEY-----\n(.+?)\n-----END RSA PUBLIC KEY-----/s")
uuid_hex = Field(pattern=r"^[0-9a-f]{8}[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{12}$")

class BasicCredentials(BaseModel):
    user_id: str = label
    password: str = password

class User(BaseModel):
    user_id: str = label

class UserDelete(BaseModel):
    user_id: str = label
    hash_hex: str = argon2_hash_hex
    
class UserUpdate(BaseModel):
    hash_hex: Optional[str] = Field(default=None, pattern=hash_hex_r)
    display_name: Optional[str] = Field(default=None, min_length=label_lengths[0], max_length=label_lengths[1], pattern=ascii_r)
    biography: Optional[str] = Field(default=None, max_length=4000)
    preferences: Optional[str] = Field(default=None)
    preferences_channels: Optional[str] = Field(default=None)
    preferences_conversations: Optional[str] = Field(default=None)
    preferences_rooms: Optional[str] = Field(default=None)

class Room(BaseModel):
    uuid: str = uuid_hex
    user_id: Optional[str] = Field(default=None, min_length=label_lengths[0], max_length=label_lengths[1], pattern=ascii_r) #ASCII
    private_key: Optional[str] = Field(default=None, pattern=r"^-----BEGIN RSA PRIVATE KEY-----\s*.*\s*-----END RSA PRIVATE KEY-----$")

class TitleRoom(BaseModel):
    title: str = label
    private_key: str = private_key

class UUIDRoom(BaseModel):
    uuid: str = uuid_hex
    user_id: str = label
    private_key: str = private_key

class RoomUpdate(BaseModel):
    uuid_room: UUIDRoom
    settings: Optional[str] = None
    permissions: Optional[str] = None

class Member(BaseModel):
    uuid_room: UUIDRoom
    member: str = label

class BanMember(BaseModel):
    uuid_room: UUIDRoom
    member: Member
    expiry_day: Optional[int] = None
    expiry_month: Optional[int] = None
    expiry_year: Optional[int] = None

class Channel(BaseModel):
    user_id: str = label
    uuid: str = uuid_hex
    private_key: str = private_key

class ChannelCreate(BaseModel):
    title: str = label
    room_uuid: str = uuid_hex
    voice_channel: bool
    public_key: str = public_key

class ChannelDelete(BaseModel):
    channel_model: Channel
    public_key: str = public_key
    room_uuid: str = uuid_hex

class ChannelUpdate(BaseModel):
    channel_model: Channel
    settings: Optional[str] = None
    permissions: Optional[str] = None

class MessageCreate(BaseModel):
    body: str = body
    channel_uuid: str = uuid_hex
    private_key: str = private_key
    public_key: str = public_key

class MessageDelete(BaseModel):
    uuid: str = uuid_hex
    private_key: str = private_key

class MessageEdit(BaseModel):
    body: str = body
    uuid: str = uuid_hex
    channel_uuid: str = uuid_hex
    private_key: str = private_key
    public_key: str = public_key

class Invite(BaseModel):
    uuid: str = uuid_hex
    passcode: str = password

class InviteAccept(BaseModel):
    uuid: str = uuid_hex
    passcode: str = password

class InviteCreate(BaseModel):
    uuid: str = uuid_hex
    passcode: str = password
    type: str = invite_type
    expiry: int = Field(ge=60, le=31556)
    invite_parameters: Optional[list] = None

class InviteParameters0(BaseModel):
    from_user_id: str = label
    to_user_id: str = label

class InviteParameters1(BaseModel):
    uuid: str = uuid_hex
    private_key: str = private_key

class Conversation(BaseModel):
    uuid: str = uuid_hex
    private_key: str = private_key

class ConversationCreate(BaseModel):
    target: str = label

class OAuth2(BaseModel):
    user_id: str = label
    password: str = password
    expiry_minutes: int = expiry
