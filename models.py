import datetime

import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
DB_URI = 'sqlite:///app.db'
engine = sqlalchemy.create_engine(DB_URI, echo=True)
Session = sqlalchemy.orm.sessionmaker(bind=engine)


class Client(Base):
    __tablename__ = 'client'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    transaction_accounts = relationship("TransactionAccount", backref="client",
                                        lazy='dynamic')

    def __repr__(self):
        return f'id: {self.id}, username: {self.username}, password: {self.password}'


class Currency(Base):
    __tablename__ = 'currency'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    code = Column(String, nullable=False, unique=True)

    transaction_accounts = relationship('TransactionAccount', backref='currency',
                                        lazy='dynamic')


class TransactionAccount(Base):
    __tablename__ = 'transaction_account'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('client.id'), nullable=False)
    currency_id = Column(Integer, ForeignKey('currency.id'), nullable=False)
    balance = Column(Integer, nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'id: {self.id}, currency_id: {self.currency_id}'


class TransactionHistory(Base):
    __tablename__ = 'transaction_history'

    id = Column(Integer, primary_key=True)
    sourse = Column(Integer, ForeignKey('transaction_account.id'), nullable=False)
    destination = Column(Integer, ForeignKey('transaction_account.id'), nullable=False)
    amount = Column(Integer, nullable=False)
    commission = Column(Integer, nullable=False)
    bonus = Column(Integer, nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


if __name__ == "__main__":
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = Session()
    session.add(Currency(name='USD', code='840'))
    session.add(Currency(name='RUB', code='643'))
    session.commit()
