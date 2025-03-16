import endpoints

map = { #Tüm endpoint isimleri karşılık geldikleri classlara eşleştirilecek.
    "channel": {
        "channel": endpoints.channel.channel.endpoint
    },
    "friend_request": {
        "friend_request": endpoints.friend_request.friend_request.endpoint,
        "accept": endpoints.friend_request.accept.endpoint,
        "cancel": endpoints.friend_request.cancel.endpoint,
        "decline": endpoints.friend_request.decline.endpoint,
        "send": endpoints.friend_request.send.endpoint
    },
    "message": {

    },
    "room": {
        "room": endpoints.room.room.endpoint,
        "create": endpoints.room.create.endpoint,
        "create_channel": endpoints.room.create_channel.endpoint,
        "delete": endpoints.room.delete.endpoint,
        "join": endpoints.room.join.endpoint,
        "updadte": endpoints.room.update.endpoint
    },
    "room_invite": {

    },
    "session": {
        "session": endpoints.session.session.endpoint,
        "new": endpoints.session.new.endpoint,
        "terminate": endpoints.session.terminate.endpoint
    },
    "status": {
        "status": endpoints.status.status.endpoint,
        "past_announcements": endpoints.status.past_announcements.endpoint,
        "time": endpoints.status.time
    },
    "user": {
        "user": endpoints.user.user.endpoint,
        "create": endpoints.user.create.endpoint,
        "delete": endpoints.user.delete.endpoint,
        "update": endpoints.user.update.endpoint
    }
}