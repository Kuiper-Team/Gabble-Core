#[7203, 7214] aralığındaki portlar bilinen başka hizmetler tarafından kullanılmıyor.
app_name = "Sohbet"

class TextChannel:
    host = "0.0.0.0"
    port = 7203
text_channel = TextChannel()

class Database:
    file_name = "database"
    default_settings = "" #Henüz hazır değil. Virgülle ayrılacak.
database = Database()