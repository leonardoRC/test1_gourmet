import datetime
from peewee import *
import logging
log_models = logging.getLogger(__name__ + ' - Model')
db = SqliteDatabase('transactions.db')

class Sequences(Model):
    """
    This class create sequences referenced by description (unique)
    """

    desc = CharField()
    pub = DateField()                                           #save the last change

    class Meta:
        database = db

class Transactions(Model):
    """
        This class create transactions table, (transactions don't need be part of a sequence)
    """
    desc = CharField()                                          #description
    date = DateField()                                          #date of transaction
    amount = FloatField()                                       #amount
    pub = DateField()                                           #save the last change
    sequence = ForeignKeyField(Sequences, null=True,)           #link to sequences

    class Meta:
        database = db


def create_tables():
    db.close()
    db.connect()
    db.create_tables([Sequences,Transactions,])
    log_models.warning('All tables created')
    db.close()

if __name__ == "__main__":
    """
    Run this file to create the database and tables
        This will create a database SQlite file named transactions.db 
    """
    create_tables()
