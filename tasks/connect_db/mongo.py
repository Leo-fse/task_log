import pymongo
from pymongo import collection
# import settings

# host = settings.MONGO_HOST
# port = settings.MONGO_PORT
# user = "USER"
# pswd = "PASSWORD"

host = 'localhost'
port = 27017

def authenticate(func):
    def wrapper(*args, **kwargs):
        print('ここに認証の処理を書く')
        func(*args, **kwargs)
        print('ここに認証を抜ける処理を書く')
    return wrapper


@authenticate
def save_data(db_name: str, collection_name: str, data, isDel: bool = False):
    client = pymongo.MongoClient(host, port)
    db = client[db_name]
    collection = db[collection_name]
    if isDel:
        collection.delete_many(filter={})
    collection.insert_many(data)
    client.close()


if __name__ == "__main__":
    data = [{"A": 1}]
    save_data("db", "collection", data)
