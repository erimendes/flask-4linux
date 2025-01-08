import montydb

# def get_conn(database):
#     client = montydb.MontyClient()
#     return client.database(database)

def get_conn(database):
    client = montydb.MontyClient()
    return client[database]
