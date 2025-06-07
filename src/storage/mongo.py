from pymongo import MongoClient

class MongoContextSource:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db['context_blocks']

    def write_blocks(self, blocks):
        docs = [b.to_dict() for b in blocks]
        self.collection.insert_many(docs)

    def find_blocks(self, query: dict):
        return list(self.collection.find(query))
