#This script is dedicated to room and channel permissions. The system uses bitwise permissions.
from enum import Enum

#Note: Each attribute has a ".name" and ".value".
class Read(Enum):
    channels = 0b1
    past_messages = 0b10
class Write(Enum):
    channels = 0b100
    invites = 0b1000
    messages = 0b10000 #Send messages
    server_data = 0b100000
    tags = 0b1000000
class Moderation(Enum):
    kick = 0b10000000
    ban = 0b100000000
class VoiceChat(Enum):
    join = 0b1000000000
    speak = 0b10000000000
    video = 0b100000000000

def check(permissions, masks: tuple):
    result = 0
    for mask in masks:
        result = permissions & mask

    return False if result == 0 else True