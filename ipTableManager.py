__author__ = 'ravi'

import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound
from ConfigReader import get_config
import pytz

DATABASE_URI = "postgresql://postgres:postgres@localhost/syssec"
engine = create_engine(DATABASE_URI, echo=False)
session = sessionmaker(bind=engine)()
Base = declarative_base()


# An orm Reflecting the Database Table in the postgres
# Internal class. Do not import this
class _BlockedIpInfo(Base):
    __tablename__ = 'blocked_ip'
    id = Column(Integer, primary_key=True)
    client_ip = Column(String)
    block_start = Column(DateTime(timezone = True))
    force_remove = Column(Boolean)


# An orm Reflecting the Database Table in the postgres
# Internal class. Do not import this
class _IPHits(Base):
    __tablename__ = 'ip_hits'
    id = Column(Integer, primary_key=True)
    client_ip = Column(String)
    hit_time = Column(DateTime(timezone = True))


# Returns all the Ips marked for Deletion.
# Also removes these specific entries from the DB
def get_ip_to_unblock():
    ips_to_unblock = session.query(_BlockedIpInfo.client_ip).filter(_BlockedIpInfo.force_remove == True).all()
    return ips_to_unblock

def delete_blocked_entries (ip_list) :
    query = session.query(_BlockedIpInfo).filter(_BlockedIpInfo.client_ip.in_(ip_list)).delete(synchronize_session=False)
    session.commit()

def process_new_ip(new_ip):
    is_blocked = False
    _add_new_ip(session,new_ip);
    config = get_config()
    diff = config.time_duration;
    current_time = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)

    d_min_ago = current_time - datetime.timedelta(minutes=diff)

    hits_last_d_mins = session.query(_IPHits).filter(_IPHits.client_ip == new_ip).filter(\
                            _IPHits.hit_time >= d_min_ago).all()


    print(len(hits_last_d_mins))
    if len(hits_last_d_mins) >= config.threshold_retries:
        is_blocked_before = _add_new_block_ip(session, new_ip)

        to_delete = session.query(_IPHits).filter(_IPHits.client_ip == new_ip).filter(\
                            _IPHits.hit_time >= d_min_ago)
        to_delete.delete();
        is_blocked = True;

    session.commit()

    return is_blocked and not is_blocked_before;


def remove_stale_entries():
    current_time = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    config = get_config()
    diff = config.time_duration;
    d_min_ago = current_time - datetime.timedelta(minutes=diff)
    session.query(_IPHits).filter(\
                            _IPHits.hit_time <= d_min_ago).delete()
    session.commit()


def mark_blocked_ip_for_removal():
    current_time = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    config = get_config()
    diff = config.block_time;
    d_min_ago = current_time - datetime.timedelta(minutes=diff)

    session.query(_BlockedIpInfo).filter(\
                            _BlockedIpInfo.block_start <= d_min_ago).update({_BlockedIpInfo.force_remove:True})
    session.commit()


def _add_new_block_ip(session, new_ip) :
    is_blocked = False;
    try :
        blockedIpInfo = session.query(_BlockedIpInfo).filter(_BlockedIpInfo.client_ip == new_ip).one()
    except NoResultFound as e :
        blockedIpInfo = None

    if blockedIpInfo == None:
        block_start = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        newEntry = _BlockedIpInfo(client_ip = new_ip, block_start = block_start, force_remove = False)
        session.add(newEntry)
    else:
      blockedIpInfo.block_start = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
      is_blocked = True

    session.commit()
    return is_blocked


def _add_new_ip(session, new_ip) :
    hit_time = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    newEntry = _IPHits(client_ip = new_ip,hit_time = hit_time);
    session.add(newEntry)
    session.commit()



# for testing purposes
if __name__ == '__main__' :
    process_new_ip("127.0.0.1")
    ip_to_unblock = get_ip_to_unblock()
    delete_blocked_entries(ip_to_unblock)
    remove_stale_entries()
    mark_blocked_ip_for_removal()
    print(ip_to_unblock)