class MockDB:
    def connect(self):
        return False
    
    def get_collection(self, name):
        return None


mongodb = MockDB()