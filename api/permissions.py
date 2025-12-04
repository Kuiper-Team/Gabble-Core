from configuration import permissions

export = {} #Usage: export["permission/code"]

def initialize():
    index = 0
    for permission in permissions:
        export.update(
            {
                permission: 1 << index
            }
        )

def check(permissions, mask: int):
    return False if permissions & mask == 0 else True