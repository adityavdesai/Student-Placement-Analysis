from flask_login import UserMixin


class Student(UserMixin):
    """
        Student object class
    """

    _id: int = -1
    name: str = ""
    email: str = ""
    password: str = ""
    type = "student"

    def __init__(self, _id: int, name: str, email: str, password: str, type: str):
        self._id = _id
        self.name = name
        self.email = email
        self.password = password

    def get_id(self):
        return self.email if self is not None else None

    def __repr__(self):
        return '%r' % [self.name, self.email, self.type]


class Hirer(UserMixin):
    """
        Hirer object class
    """

    _id: int = -1
    name: str = ""
    email: str = ""
    password: str = ""
    company: str = ""
    type = "hirer"

    def __init__(self, _id: int, name: str, company: str, email: str, password: str, type: str):
        self._id = _id
        self.name = name
        self.company = company
        self.email = email
        self.password = password

    def get_id(self):
        return self.email if self is not None else None

    def __repr__(self):
        return '%r' % [self.name, self.company, self.email, self.type]
