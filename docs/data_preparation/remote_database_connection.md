# Remote database connection
Some data preparation operations require a connection to a remote database. For this purpose it is necessary to make certain connection settings. 

Some data preparation operations require a connection to a remote database. For this purpose it is necessary to make certain connection settings. This can be done in the file _"db.yaml"_ located in the folder _"config"_. It is necessary to specify the data for the remote connection in the second part of the settings. The first part refers to the Docker database. After the settings are made, it is possible to interact with the remote database given in fusion.

```yaml
...
HOST: "localhost"
PORT: 55432
DB_NAME: "goat"
USER: "goat"
PASSWORD: "earlmanigault"

# Remote DB connection creditentials
HOST_RD: "remote_db_host"
PORT_RD: 5432
DB_NAME_RD: "remote_db_name"
USER_RD: "remote_db_user_name"
PASSWORD_RD: "remote_db_password"
```