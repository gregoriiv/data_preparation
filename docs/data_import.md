# How to import data?

## Manual import

### Import SQL dump
1. SSH into docker container
`docker exec -it /bin/bash db_data_preparation`

2. Restore 
`psql -U goat -d goat -f path-to-your-file.sql`

