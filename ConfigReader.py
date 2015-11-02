from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound

DATABASE_URI = "postgresql://postgres:postgres@localhost/syssec"
engine = create_engine(DATABASE_URI, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# An orm Reflecting the Database Table in the postgres
# Internal class. Do not import this
class _ConfigReader(Base) :
    __tablename__ = 'configuration_table'
    id = Column(Integer, primary_key=True)
    time_duration = Column(Integer)
    threshold_retries = Column(Integer)
    block_time = Column(Integer)

# This is the class that is constructed and given outside
# Incase we decide to cache the data for a given amount of time
# we can cache this class


class Config :
    def __init__(self, time_duration, threshold_retries, block_time) :
        self.time_duration = time_duration
        self.threshold_retries = threshold_retries
        self.block_time = block_time

    def __str__(self):
        return str([self.time_duration, self.threshold_retries, self.block_time ])

    def __unicode__(self):
        return str([self.time_duration, self.threshold_retries, self.block_time ])


# Call this method for Configuration
def get_config():
    session = Session()
    query = session.query(_ConfigReader)
    try:
        configDbEntry = query.one()
    except MultipleResultsFound, e:
        print e
    return Config(configDbEntry.time_duration, configDbEntry.threshold_retries, configDbEntry.block_time)


# for testing purposes
if __name__ == '__main__' :
    config = get_config()
    print(config)


