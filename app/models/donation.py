from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import CharityBase


class Donation(CharityBase):
    user_id = Column(
        Integer,
        ForeignKey('user.id', name='fk_donation_user_id_user')
    )
    comment = Column(Text)

    def __repr__(self):
        return (f"<Donation("
                f"{super().__repr__()}, "
                f"user_id='{self.user_id}', "
                f"comment='{self.comment}')>")
