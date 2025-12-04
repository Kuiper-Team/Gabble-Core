#This script is dedicated to room and channel permissions. The system uses bitwise permissions.
from enum import Enum

from configuration import permissions

export = {}

def initialize():
    index = 0
    for permission in permissions:
        export.update(
            {
                permission: 1 << index
            }
        )

def check(permissions, mask: int): #mask example: Read.channels
    return False if permissions & mask == 0 else True