"""
This module implements the printer data related database models.
"""

__author__ = "Marc Bermejo"
__credits__ = ["Marc Bermejo"]
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Marc Bermejo"
__email__ = "mbermejo@bcn3dtechnologies.com"
__status__ = "Development"

from datetime import datetime, timedelta

from .table_names import (
    PRINTER_MODELS_TABLE, PRINTER_STATES_TABLE, PRINTER_EXTRUDER_TYPES_TABLE,
    PRINTER_MATERIALS_TABLE, PRINTER_EXTRUDERS_TABLE, PRINTERS_TABLE, JOBS_TABLE
)
from ..definitions import db_conn as db, bind_key


class PrinterModel(db.Model):
    """
    Definition of table PRINTER_MODELS_TABLE that contains the printer known models.
    """
    __bind_key__ = bind_key
    __tablename__ = PRINTER_MODELS_TABLE

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(256), unique=True, nullable=False)
    width = db.Column(db.Float, nullable=False)
    depth = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)

    printers = db.relationship('Printer', back_populates='model')

    def __repr__(self):
        return '[{}]<id: {} / name: {}>'.format(self.__tablename__, self.id, self.name)


class PrinterState(db.Model):
    """
    Definition of table PRINTER_STATES_TABLE that contains the printer known states.
    """
    __bind_key__ = bind_key
    __tablename__ = PRINTER_STATES_TABLE

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    stateString = db.Column(db.String(256), unique=True, nullable=False)
    isOperationalState = db.Column(db.Boolean, nullable=False)

    printers = db.relationship('Printer', back_populates='state')

    def __repr__(self):
        return '[{}]<id: {} / stateString: {}>'.format(self.__tablename__, self.id, self.stateString)


class PrinterExtruderType(db.Model):
    """
    Definition of table PRINTER_EXTRUDER_TYPES_TABLE that contains the printer known extruder types.
    """
    __bind_key__ = bind_key
    __tablename__ = PRINTER_EXTRUDER_TYPES_TABLE

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    brand = db.Column(db.String(256))
    nozzleDiameter = db.Column(db.Float, nullable=False)

    extruders = db.relationship('PrinterExtruder', back_populates='type')
    jobs = db.relationship('JobAllowedExtruder', back_populates='type')

    def __repr__(self):
        return '[{}]<id: {} / brand: {} / nozzleDiameter: {}>'.format(self.__tablename__, self.id,
                                                                      self.brand, self.nozzleDiameter)


class PrinterMaterial(db.Model):
    """
    Definition of table PRINTER_MATERIALS_TABLE that contains all known printable materials.
    """
    __bind_key__ = bind_key
    __tablename__ = PRINTER_MATERIALS_TABLE

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    type = db.Column(db.String(32), nullable=False)
    color = db.Column(db.String(32))
    brand = db.Column(db.String(256))
    GUID = db.Column(db.String(256))
    printTemp = db.Column(db.Float, nullable=False)
    bedTemp = db.Column(db.Float, nullable=False)

    extruders = db.relationship('PrinterExtruder', back_populates='material')
    jobs = db.relationship('JobAllowedMaterial', back_populates='material')

    def __repr__(self):
        return '[{}]<id: {} / type: {}>'.format(self.__tablename__, self.id, self.type)


class PrinterExtruder(db.Model):
    """
    Definition of table PRINTER_EXTRUDERS_TABLE that contains printer extruders information.
    """
    __bind_key__ = bind_key
    __tablename__ = PRINTER_EXTRUDERS_TABLE

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    idPrinter = db.Column(db.Integer, db.ForeignKey(PRINTERS_TABLE + '.id'), nullable=False)
    idExtruderType = db.Column(db.Integer, db.ForeignKey(PRINTER_EXTRUDER_TYPES_TABLE + '.id'))
    idMaterial = db.Column(db.Integer, db.ForeignKey(PRINTER_MATERIALS_TABLE + '.id'))
    index = db.Column(db.Integer, nullable=False)

    type = db.relationship('PrinterExtruderType', back_populates='extruders', uselist=False)
    material = db.relationship('PrinterMaterial', back_populates='extruders', uselist=False)
    printer = db.relationship('Printer', back_populates='extruders', uselist=False)

    def __repr__(self):
        # position = "right" if self.index == 0 else "left"
        return '[{}]<idPrinter: {} / idExtruderType: {} / idMaterial: {} / index: {}>'.\
            format(self.__tablename__, self.idPrinter, self.idExtruderType, self.idMaterial, self.index)


class Printer(db.Model):
    """
    Definition of table PRINTERS_TABLE that contains the printers information.
    """
    __bind_key__ = bind_key
    __tablename__ = PRINTERS_TABLE

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    idModel = db.Column(db.Integer, db.ForeignKey(PRINTER_MODELS_TABLE + '.id'), nullable=False)
    idState = db.Column(db.Integer, db.ForeignKey(PRINTER_STATES_TABLE + '.id'), nullable=False)
    idCurrentJob = db.Column(db.Integer, db.ForeignKey(JOBS_TABLE + '.id'))
    name = db.Column(db.String(256), unique=True, nullable=False)
    serialNumber = db.Column(db.String(256), unique=True, nullable=False)
    ipAddress = db.Column(db.String(16))
    sid = db.Column(db.String(64))
    registeredAt = db.Column(db.DateTime, default=datetime.now, nullable=False)
    totalSuccessPrints = db.Column(db.Integer, nullable=False, default=0)
    totalFailedPrints = db.Column(db.Integer, nullable=False, default=0)
    totalPrintingTime = db.Column(db.Interval, nullable=False, default=timedelta())

    model = db.relationship('PrinterModel', back_populates='printers', uselist=False)
    state = db.relationship('PrinterState', back_populates='printers', uselist=False)
    extruders = db.relationship('PrinterExtruder', back_populates='printer', cascade="all, delete-orphan",
                                order_by='PrinterExtruder.index')
    current_job = db.relationship('Job', back_populates='assigned_printer', uselist=False)

    def __repr__(self):
        is_operative = self.state.isOperationalState
        return '[{}]<id: {} / serialNumber: {} / isOperative: {}>'.format(self.__tablename__, self.id,
                                                                          self.serialNumber, is_operative)
