#[7203, 7214] aralığındaki portlar bilinen başka hizmetler tarafından kullanılmıyor.
app_name = "Sohbet"

class UserConnection:
    host = "0.0.0.0"
    port = 7203
user_connection = UserConnection()

class Database:
    file_name = "database"
    default_user_settings = "" #Henüz hazır değil. Virgülle ayrılacak.
    default_channel_pm = ""
    default_group_pm = ""
database = Database()

class Message:
    character_limit = 4000
message = Message()