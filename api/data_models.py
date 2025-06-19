from pydantic import BaseModel, Field

username = Field(min_length=3, max_length=36)
hash = Field(min_length=64, max_length=64, pattern=r"^[A-Fa-f0-9]{64}$")

class BasicCredentials(BaseModel):
    username: str = username
    password: str = Field(min_length=10, max_length=48, pattern=r"^[\x00-\x7F]*$")

class HashCredentials(BaseModel):
    username: str = username
    hash: str = hash

class UserUpdate(BaseModel):
    hash_credentials: HashCredentials
    display_name: str = None
    channel_settings: str = None
    settings: str = None
    room_settings: str = None