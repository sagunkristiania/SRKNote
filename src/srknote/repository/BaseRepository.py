

from ..config.base import Base
# CREATE USER

class BaseRepository:
    def __init__(self, model, db):
        self.db = db
        self.model = model