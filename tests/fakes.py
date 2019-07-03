from tapeworm.model_link import Link


class FakeLinks:
    def __init__(self):
        self.links = []

    def from_dict(self, data):
        """
        Creates a Link from a dictionary. The output from this function
        can be passed into create with Link._asdict()
        """
        if not isinstance(data, dict):
            raise ValueError("data must be type of dict")
        if not data:
            raise ValueError("data must be valid")

        return Link(
            id=None,
            link=data["link"],
            title=data["title"],
            by=data["by"],
            date=data["date"],
        )

    def create_multi(self, datas):
        if not isinstance(datas, list):
            raise ValueError("datas must be type of List containing Link")
        self.links = self.links + datas
        return datas

    def list_links(self):
        return self.links
