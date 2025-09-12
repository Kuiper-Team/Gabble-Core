from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import ClassVar

body = Field(min_length=1, max_length=10000)
base64 = Field(min_length=1, pattern="^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$")
invite_type = Field(max_length=1, pattern=r"(f|r)")
label = Field(min_length=3, max_length=36, pattern=r"[^,]+")
password = Field(min_length=12, max_length=72, pattern=r"^[\x00-\x7F]*$")
private_key = Field(pattern=r"^-----BEGIN RSA PRIVATE KEY-----\s*.*\s*-----END RSA PRIVATE KEY-----$")
public_key = Field(pattern=r"/-----BEGIN RSA PUBLIC KEY-----\n(.+?)\n-----END RSA PUBLIC KEY-----/s")
uuid_hex = Field(min_length=32, max_length=32, pattern=r"^[0-9a-f]{8}[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{4}[0-9a-f]{12}$")

class Username(BaseModel):
    username: str = label

class BasicCredentials(BaseModel):
    username: str = label
    password: str = password

class HashCredentials(BaseModel):
    username: str = label
    hash: str = base64

class UserUpdate(BaseModel):
    hash_credentials: HashCredentials
    display_name: ClassVar[str] = None
    channel_settings: ClassVar[str] = None
    settings: ClassVar[str] = None
    room_settings: ClassVar[str] = None

class Room(BaseModel):
    hash_credentials: HashCredentials
    uuid: str = uuid_hex

class TitleRoom(BaseModel):
    hash_credentials: HashCredentials
    title: str = label
    private_key: str = private_key

class UUIDRoom(BaseModel):
    hash_credentials: HashCredentials
    uuid: str = uuid_hex
    private_key: str = private_key

class RoomUpdate(BaseModel):
    hash_credentials: HashCredentials
    uuid_room: UUIDRoom
    settings: ClassVar[str] = None
    permissions: ClassVar[str] = None

class Member(BaseModel):
    hash_credentials: HashCredentials
    uuid_room: UUIDRoom
    member: str = label

class BanMember(BaseModel):
    hash_credentials: HashCredentials
    member: Member
    expiry_day: ClassVar[int] = None
    expiry_month: ClassVar[int] = None
    expiry_year: ClassVar[int] = None

class Channel(BaseModel):
    hash_credentials: HashCredentials
    username: str = label
    uuid: str = uuid_hex
    private_key: str = private_key

class ChannelCreate(BaseModel):
    hash_credentials: HashCredentials
    title: str = label
    room_uuid: str = uuid_hex
    voice_channel: bool
    public_key: str = public_key

class ChannelDelete(BaseModel):
    hash_credentials: HashCredentials
    channel_model: Channel
    public_key: str = public_key
    room_uuid: str = uuid_hex

class ChannelUpdate(BaseModel):
    hash_credentials: HashCredentials
    channel_model: Channel
    settings: ClassVar[str] = None
    permissions: ClassVar[str] = None

class MessageCreate(BaseModel):
    hash_credentials: HashCredentials
    body: str = body
    channel_uuid: str = uuid_hex
    private_key: str = private_key
    public_key: str = public_key

class MessageDelete(BaseModel):
    hash_credentials: HashCredentials
    uuid: str = uuid_hex
    private_key: str = private_key

class MessageEdit(BaseModel):
    hash_credentials: HashCredentials
    body: str = body
    uuid: str = uuid_hex
    channel_uuid: str = uuid_hex
    private_key: str = private_key
    public_key: str = public_key

class Invite(BaseModel):
    hash_credentials: HashCredentials
    uuid: str = uuid_hex
    passcode: str = password

class InviteAccept(BaseModel):
    hash_credentials: HashCredentials
    uuid: str = uuid_hex
    passcode: str = password
    private_key: str = private_key

class InviteCreate(BaseModel):
    hash_credentials: HashCredentials
    uuid: str = uuid_hex
    passcode: str = password
    type: str = invite_type
    expiry: int = Field(ge=60, le=31556)
    target: ClassVar[None] = None
    room_uuid: ClassVar[None] = None

class InviteDecline(BaseModel):
    hash_credentials: HashCredentials
    uuid: str = uuid_hex
    passcode: str = password
    type: str = invite_type

class Conversation(BaseModel):
    hash_credentials: HashCredentials
    uuid: str = uuid_hex
    private_key: str = private_key

class ConversationCreate(BaseModel):
    hash_credentials: HashCredentials
    target: str = label

class OAuth2(BaseModel):
    uuid: str = label
    hash: str = base64
    expiry_minutes: int

class OAuth2ID(BaseModel):
    uuid: str = label
    hash: str = base64