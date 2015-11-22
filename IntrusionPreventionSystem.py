import ipTableManager
import sys, time
import threading
import subprocess
import re
from ConfFileReader import ConfFileReader
from Queue import Queue

# Key: IP address
# Value: [start_time, count, block_start, force_remove]
# force_remove: is for those IP addresses which are unblocked by the admin
#               which is basically removing the IP Table entry
iptable={}
NWORKS = 10

# Synchronization primitives
lock = threading.RLock()
fullCondition = threading.Condition(lock)
# Work Queue
queue = []
wque = Queue(NWORKS)
credentials = {}
applications = {}

# Helper functions
def is_user_pass_line(line, list_user_pass_keywords):
    for keyword in list_user_pass_keywords:
        pattern = re.compile(keyword)
        if pattern.search(line):
            return True
    return False

def get_application_name(line, list_user_pass_keywords):
    global applications
    if not applications:
        return None
    for keyword in list_user_pass_keywords:
        pattern = re.compile(keyword)
        if pattern.search(line):
            return applications[keyword]
    return None

def get_candidate_for_login_failure(line, login, logout, ip_regex):
    state = False
    global credentials
    if not line:
        return None
    login_pattern = re.compile(login)
    logout_pattern = re.compile(logout)
    ip_pattern = re.compile(ip_regex)
    if login_pattern.search(line):
        ip_port_tuple = ip_pattern.search(line)
        if ip_port_tuple:
            return [ip_port_tuple.groups()[0], True]
    elif logout_pattern.search(line):
        ip_port_tuple = ip_pattern.search(line)
        if ip_port_tuple:
            return [ip_port_tuple.groups()[0], False]
    return None

def get_candidate_for_failure(fd, line, application, user_pass_pattern, ip_regex):
    global credentials
    if not line or not credentials:
        return None
    pattern = re.compile(user_pass_pattern)
    if pattern.search(line):
        user_pass_tuple=pattern.search(line)
        if user_pass_tuple:
            # Checking the user and password credentials
            if credentials[application][0] != user_pass_tuple.groups()[0] or credentials[application][1] != user_pass_tuple.groups()[1]:
                # Login failure
                # Get the IP from the next line
                next_line = fd.readline().strip()
                ip_pattern = re.compile(ip_regex)
                ip_tuple = ip_pattern.search(next_line)
                if ip_tuple:
                    return ip_tuple.groups()
    return None

def get_ip_from_line(line, regex, ip_port_regex):
    if not line:
        return None
    pattern = re.compile(regex)
    if pattern.search(line):
        # Found a match - Authentication Failure
        ip_pattern = re.compile(ip_port_regex)
        ip_port_tuple = ip_pattern.search(line)
        if ip_port_tuple:
            return ip_port_tuple.groups()
    return None

def unblocking():
    # Reads the force_remove value of the IP table
    # If its true: remove the entry from the system IPTable
    # If not do nothing
    print "Unblocking the ip addr..!!"
    fail = False
    # Monitoring thread, runs indefinitely
    # 1. Cleans-up the DB
    # 2. Unblocks the IPs
    while True:
        print "[Unblock] Thread woke up..!!"
        ipTableManager.mark_blocked_ip_for_removal()
        ipTableManager.remove_stale_entries()
        unblocked_ips = ipTableManager.get_ip_to_unblock()
        for ip in unblocked_ips:
            # Make sure that allowBlock.sh is in the same directory as this script
            # And also PATH variable is exported with current working directory appended to the PATH
            try:
                subprocess.call(["./allowBlock.sh", str(ip[0]), "ALLOW"])
                print "[Unblocking] Successfully unblocked: ", str(ip[0])
            except:
                print "[Unblocking] Unblocking on ", str(ip[0]), " failed.!"
                fail = True

        if fail == False:
            # Call delete entries operations to cleanup the DB
            ipTableManager.delete_blocked_entries(unblocked_ips)

        # Sleep for 10 seconds before the next run
        time.sleep(10)

class Consumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # Read from the configuration file
        # Get the thresholds
        # Validate against the current ip address
        global fullCondition, queue, lock

        # Consumer thread, runs indefinitely
        # 1. Waits on the queue
        # 2. Upon the notify of cond var, makes an entry to DB
        # 3. Decided whether to Block the IP based on the threshold conditions
        # 4. Wakes-up the Producer thread to add entries to the queue

        while True:
            print "In Consumer dude, waiting to acquire lock"
            fullCondition.acquire()
            print "Consumer, acquired the lock"
            if not queue:
                print "In cond wait of consumer.!"
                fullCondition.wait()
            print "Consumer came out of wait..!!!!"
            ipaddr = queue.pop(0) # A (IP, Port) tuple
            print "Consuming..!! IP: ", ipaddr
            if ipTableManager.process_new_ip(ipaddr[0]) == True:
                # Block the IP
                try:
                    subprocess.call(["./allowBlock.sh", ipaddr[0], "DROP"])
                    print "[Consumer] Successfully blocked: ", ipaddr[0]
                except:
                    print "**** [Consumer] Blocking ", ipaddr[0], " Failed ", sys.exc_info()[0]
            fullCondition.notify()
            fullCondition.release()
            # time.sleep(1)
        print "Consumer End..!! IP: ", ipaddr[0]

class consumer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            if not wque.empty():
                print "Consumer came out of wait..!!!! Queue: ", wque.queue
                ipaddr = wque.get(1) # A (IP, Port) tuple
                print "Consuming..!! IP: ", ipaddr, " rem : ", wque.queue
                if ipTableManager.process_new_ip(ipaddr[0], ipaddr[1], ipaddr[2]) == True:
                    # Block the IP
                    try:
                        subprocess.call(["./allowBlock.sh", ipaddr[0], "DROP"])
                        print "[Consumer] Successfully blocked: ", ipaddr[0]
                    except:
                        print "**** [Consumer] Blocking ", ipaddr[0], " Failed ", sys.exc_info()[0]
                time.sleep(1)

class producer_apache(threading.Thread):
    def __init__(self, filename, login,  logout, ip_pat, appl_name):
        threading.Thread.__init__(self)
        self.filename = filename
        self.login_pattern = login
        self.logout_pattern = logout
        self.ip_pattern = ip_pat
        self.appl_name = appl_name

    def run(self):
        try:
            fileDesc = open(self.filename, "r")
            # fileDesc = open("./auth.log", "r")
            fileDesc.seek(0,2)
            while True:
                if not wque.full():
                    # Get the line from the log file
                    # Check if the authentication failed
                    # Obtain the IP address from the line to block
                    line = fileDesc.readline().strip()
                    # Parameters:
                    # param1: File descriptor of the file
                    # param2: line from the file
                    # param3: name of the application to monitor
                    # param4: pattern to identify the user name and password
                    # param5: pattern to identify the ip address
                    ip_list = get_candidate_for_login_failure(line, self.login_pattern, self.logout_pattern, self.ip_pattern)
                    if not ip_list:
                        time.sleep(0.1)
                        continue
                    else:
                        print "Producing: ", ip_list, " Queue ", wque.queue
                        # Need to add more logic to get only the IP Address, Port Tuple
                        ip_list.append(self.appl_name)
                        wque.put(ip_list)
                    time.sleep(1)
        except:
            print "File : ", self.filename, " has some issues.!"

class producer_new(threading.Thread):
    def __init__(self, filename, err_pat,  ipport_pat, appl_name):
        threading.Thread.__init__(self)
        self.filename = filename
        self.up_pattern = err_pat
        self.ip_pattern = ipport_pat
        self.appl_name = appl_name

    def run(self):
        try:
            fileDesc = open(self.filename, "r")
            # fileDesc = open("./auth.log", "r")
            fileDesc.seek(0,2)
            while True:
                if not wque.full():
                    # Get the line from the log file
                    # Check if the authentication failed
                    # Obtain the IP address from the line to block
                    line = fileDesc.readline().strip()
                    # Parameters:
                    # param1: File descriptor of the file
                    # param2: line from the file
                    # param3: name of the application to monitor
                    # param4: pattern to identify the user name and password
                    # param5: pattern to identify the ip address
                    ip = get_candidate_for_failure(fileDesc, line, self.appl_name, self.up_pattern, self.ip_pattern)
                    if not ip:
                        time.sleep(0.1)
                        continue
                    else:
                        print "Producing: ", ip, " Queue ", wque.queue
                        # Need to add more logic to get only the IP Address, Port Tuple
                        wque.put(ip)
                    time.sleep(1)
        except:
            print "File : ", self.filename, " has some issues.!"

class producer(threading.Thread):
    def __init__(self, filename, err_pat,  ipport_pat):
        threading.Thread.__init__(self)
        self.filename = filename
        self.error_pattern = err_pat
        self.ipport_pattern = ipport_pat

    def run(self):
        try:
            fileDesc = open(self.filename, "r")
            fileDesc.seek(0,2)
            while True:
                if not wque.full():
                    # print "Producer came out of wait..!!!!"
                    # Get the line from the log file
                    # Check if the authentication failed
                    # Obtain the IP address from the line to block
                    line = fileDesc.readline().strip()
                    # Parameters:
                    # param1: line from the file
                    # param2: pattern to first match in case of failure
                    # param3: pattern to identify the ip and port number
                    ip = get_ip_from_line(line, self.error_pattern, self.ipport_pattern)
                    if not ip:
                        time.sleep(0.1)
                        continue
                    else:
                        print "Producing: ", ip, " Queue ", wque.queue
                        # Need to add more logic to get only the IP Address, Port Tuple
                        wque.put([ip[0], True])
                    time.sleep(1)
        except:
            print "File : ", self.filename, " has some issues.!"

class Producer(threading.Thread):
    def __init__(self, filename, err_pat,  ipport_pat):
        threading.Thread.__init__(self)
        self.filename = filename
        self.error_pattern = err_pat
        self.ipport_pattern = ipport_pat

    def run(self):
        # Read the log file
        # Find the pattern
        # Get the IP address
        # Return it as a string
        # Logic to read the log files and update the ip
        # So that the producer will make an entry to the table
        # fileDesc = open("/var/adm/log/auth.log", "r")
        global fullCondition, queue, lock
        try:
            fileDesc = open(self.filename, "r")
            # fileDesc = open("./auth.log", "r")
            fileDesc.seek(0,2)
            while True:
                # print "In producer"
                fullCondition.acquire()
                if len(queue) >= 1:
                    # Assuming queue is full
                    print "In cond wait of producer for ", self.filename
                    fullCondition.wait()
                # Get the line from the log file
                # Check if the authentication failed
                # Obtain the IP address from the line to block
                line = fileDesc.readline().strip()
                # Parameters:
                # param1: line from the file
                # param2: pattern to first match in case of failure
                # param3: pattern to identify the ip and port number
                ip = get_ip_from_line(line, self.error_pattern, self.ipport_pattern)
                if not ip:
                    time.sleep(0.1)
                    continue
                else:
                    # Need to add more logic to get only the IP Address, Port Tuple
                    queue.append(ip)
                print "Producing: ", ip, " Queue ", queue
                fullCondition.notifyAll()
                # print "Notifying the consumer.."
                fullCondition.release()
                # print "Released..!!!"
                time.sleep(5)
        except:
            print "File : ", self.filename, " has some issues.!"

if __name__ == "__main__":
    print "Application Started.!"
    # Read the file indefinitely - log

    # lock = threading.RLock()
    #
    # t2 = ThreadLibrary(consumer, lock)
    # t3 = ThreadLibrary(unblocking, lock)
    #
    # t2.start()
    # t3.start()
    # for ipaddr in getIPAddr():
    #     # 1. Run Producer Thread
    #     # 2. Run Consumer Thread
    #     # 3. Run Unblock Thread
    #     t1 = ThreadLibrary(producer, ipaddr, lock)
    #     t1.start()
    #     print " Hi , ", ipaddr
    #     t1.stop()
    # t1.stop()
    # t2.stop()
    # t3.stop()

    # Simple producer consumer problem
    # t1 - used to read the updates from the file
    #      append the queue with the ip address
    # t2 - consumes from the queue and builds ip tables
    # t3 - unblocks the IPs based on block timeouts and admin requests

    conf_file = ConfFileReader('config/Applications.conf', 'config/Credentials.conf', 'config/ApacheRequests.conf')
    conf_file.run()
    # nproducers = len(conf_file.get_patterns())
    patterns = conf_file.get_apache_patterns()
    # patterns = conf_file.get_patterns()
    # credentials = conf_file.get_credentials()
    # for files in patterns.keys():
    nproducers = len(patterns)
    print nproducers
    for list in patterns:
        print "File ", list[0], " Patterns: ", list[1:]
        # Using Queues, implicitly has locks
        # producer(files, patterns[files][0], patterns[files][1]).start()
        if list[3] == 'ssh':
            producer(list[0], list[1], list[2]).start()
        else:
            producer_apache(list[0], list[1], list[2], list[3]).start()

    # Producer().start()
    # Consumer().start()

    # Using Queues, implicitly has locks
    consumer().start()
    ublock_thread = threading.Thread(target=unblocking)
    ublock_thread.start()
    print "Application Exitted.!"
