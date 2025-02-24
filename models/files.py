"""
This module implements the file data related database models.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from datetime import datetime

from .table_names import (
    FILES_TABLE, USERS_TABLE
)
from ..definitions import db_conn as db, bind_key


class File(db.Model):
    """
    Definition of the table FILES_TABLE that contains all the uploaded GCODE files
    """
    __bind_key__ = bind_key
    __tablename__ = FILES_TABLE

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    idUser = db.Column(db.Integer, db.ForeignKey(USERS_TABLE+'.id'), nullable=False)
    name = db.Column(db.String(256), nullable=False)
    fullPath = db.Column(db.String(256), unique=True)
    createdAt = db.Column(db.DateTime, default=datetime.now, nullable=False)
    estimatedPrintingTime = db.Column(db.Interval)
    estimatedNeededMaterial = db.Column(db.Float)
    fileData = db.Column(db.JSON)

    user = db.relationship('User', back_populates='files', uselist=False)
    jobs = db.relationship('Job', back_populates='file', cascade="all, delete-orphan")

    def __repr__(self):
        return '[{}]<id: {} / name: {}>'.format(self.__tablename__, self.id, self.name)
