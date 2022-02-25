from decouple import config

DATABASE = {
    'user':     config("POSTGRES_USER"),
    'password': config("POSTGRES_PASSWORD"),
    'host':     config("POSTGRES_HOST"),
    'port':     5432,
    'dbname':   config("POSTGRES_DB")
}

DATABASE_RD = {
    'user':     config("USER_RD"),
    'password': config("PASSWORD_RD"),
    'host':     config("HOST_RD"),
    'port':     config("PORT_RD"),
    'dbname':   config("DB_NAME_RD")
}