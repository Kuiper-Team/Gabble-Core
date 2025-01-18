#[7203, 7214] aralığındaki portlar bilinen başka hizmetler tarafından kullanılmıyor.
app_name = "Sohbet"

class Channel:
    host = "0.0.0.0"
    port = 7203
channel = Channel()

class Database:
    file_name = "database"
    default_user_settings = "000"
database = Database()