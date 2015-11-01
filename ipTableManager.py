__author__ = 'ravi'

import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound
from .ConfigReader import  get_config

DATABASE_URI = "postgresql://postgres:postgres@localhost/syssec"
engine = create_engine(DATABASE_URI, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# An orm Reflecting the Database Table in the postgres
# Internal class. Do not import this
class _BlockedIpInfo(Base):
    __tablename__ = 'ip_table'
    id = Column(Integer, primary_key=True)
    client_ip = Column(String)
    start_time = Column(DateTime)
    block_start = Column(DateTime)
    force_remove = Column(Boolean)
    count = Column(Integer)


# Returns all the Ips marked for Deletion.
# Also removes these specific entries from the DB
def get_ip_to_unblock() :
    session = Session()
    query = session.query(_BlockedIpInfo.client_ip).filter(_BlockedIpInfo.force_remove == True)
    ips_to_unblock = query.all()
    session.query(_BlockedIpInfo).filter(_BlockedIpInfo.force_remove == True).delete(synchronize_session=False)
    session.commit()
    return ips_to_unblock


def process_new_ip(new_ip) :
    session = Session()
    query = session.query(_BlockedIpInfo).filter(_BlockedIpInfo.client_ip == new_ip)

    try:
        ip_info = query.one()
    except NoResultFound, e:
        _add_new_ip(session, new_ip)
        return
    except MultipleResultsFound, e:
        print("Something wrong, multiple results with the same Ip found")

    config = get_config()
    # If already marked for deletion, Then delete it and add New Entry
    if ip_info.force_remove == False :
        session.delete(ip_info)
        _add_new_ip(session, new_ip)
        return





def _add_new_ip(session, new_ip) :
    newEntry = _BlockedIpInfo(client_ip = new_ip,start_time = datetime.datetime.utcnow, \
                                  block_start = None, force_remove = False, count =1)
    session.add(newEntry)
    session.commit()

#def mark_stale_entries()




# for testing purposes
if __name__ == '__main__' :
    ip_to_unblock = get_ip_to_unblock()
    print(ip_to_unblock)