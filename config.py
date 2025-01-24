#[7203, 7214] aralığındaki portlar bilinen başka hizmetler tarafından kullanılmıyor.
app_name = "Sohbet"

class WSTextChannel:
    host = "0.0.0.0"
    port = 7203
ws_text_channel = WSTextChannel()

class Database:
    file_name = "database"
    default_user_settings = "" #Henüz hazır değil. Virgülle ayrılacak.
    default_channel_pm = ""
    default_group_pm = ""
database = Database()