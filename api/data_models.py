from pydantic import BaseModel, Field
from typing import Optional

argon2_hash_hex = Field(pattern=r"^[0-9a-fA-F]{32}$")
argon2_hash_hex_optional = Field(pattern=r"^[0-9a-fA-F]{32}$", default=None)
body = Field(min_length=1, max_length=10000)
base64 = Field(min_length=1, pattern=r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$")
expiry = Field(ge=1, le=525600)
invite_type = Field(max_length=1, pattern=r"(f|r)")
label = Field(min_length=3, max_length=36, pattern=r"^[\x00-\x7F]*$") #ASCII
password = Field(min_length=12, max_length=72, pattern=r"^[\x00-\x7F]*$") #ASCII
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

class UserUpdate(BaseModel): #Needs fix: Optional values which use fields
    hash_hex: Optional[str]
    display_name: Optional[str]
    biography: Optional[str]
    preferences: Optional[str]
    preferences_channels: Optional[str]
    preferences_conversations: Optional[str]
    preferences_rooms: Optional[str]

class Room(BaseModel):
    uuid: str = uuid_hex

class TitleRoom(BaseModel):
    title: str = label
    private_key: str = private_key

class UUIDRoom(BaseModel):
    uuid: str = uuid_hex
    private_key: str = private_key

class RoomUpdate(BaseModel):
    uuid_room: UUIDRoom
    settings: Optional[str] = None
    permissions: Optional[str] = None

class Member(BaseModel):
    uuid_room: UUIDRoom
    member: str = label

class BanMember(BaseModel):
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
    private_key: str = private_key

class InviteCreate(BaseModel):
    uuid: str = uuid_hex
    passcode: str = password
    type: str = invite_type
    expiry: int = Field(ge=60, le=31556)
    target: Optional[None] = None
    room_uuid: Optional[None] = None

class InviteDecline(BaseModel):
    uuid: str = uuid_hex
    passcode: str = password
    type: str = invite_type

class Conversation(BaseModel):
    uuid: str = uuid_hex
    private_key: str = private_key

class ConversationCreate(BaseModel):
    target: str = label

class OAuth2(BaseModel):
    user_id: str = label
    password: str = password
    expiry_minutes: int = expiry