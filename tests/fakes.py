class FakeLinks:
    def __init__(self):
        self.links = []

    def create_multi(self, datas):
        if not isinstance(datas, list):
            raise ValueError("datas must be type of List containing Link")
        self.links = self.links + datas
        return datas

    def list_links(self, offset, limit):
        return self.links[offset : offset + limit]
