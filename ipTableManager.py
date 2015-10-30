__author__ = 'ravi'

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound

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


#def process_new_ip(new_ip) :


#def mark_stale_entries() :




# for testing purposes
if __name__ == '__main__' :
    ip_to_unblock = get_ip_to_unblock()
    print(ip_to_unblock)