from configuration import permissions

mask = {} #Example: export["read/channels"] returns the number of the permission with the id "read/channels". See configuration.py.

def initialize():
    index = 0
    for permission in permissions:
        mask.update(
            {
                permission: 1 << index
            }
        )

def check(available_permissions: int, provided_mask: int):
    return False if available_permissions & provided_mask == 0 else True