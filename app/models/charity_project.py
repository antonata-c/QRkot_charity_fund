from sqlalchemy import Column, String, Text

from app.models.base import CharityBase


class CharityProject(CharityBase):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    def __repr__(self):
        return (f"<CharityProject("
                f"{super().__repr__()}, "
                f"name='{self.name}', "
                f"description='{self.description}')>")
