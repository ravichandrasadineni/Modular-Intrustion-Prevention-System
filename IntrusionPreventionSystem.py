
import sys, time
import threading

# Key: IP address
# Value: [start_time, count, block_start, force_remove]
# force_remove: is for those IP addresses which are unblocked by the admin
#               which is basically removing the IP Table entry
iptable={}

iplist = ["1.2.3.4", "1.2.3.5", "1.2.3.6", "1.2.3.7", "1.2.3.8"]

def getThCount():
    # Read from db and return the value
    # Temporarily returning 5
    return 5

def getThBlockTicks():
    # Read from db and return the value
    # This is basically for the timeout of blocking the ip addr
    # Temporarily returning 5
    return 5

def getThTimeTicks():
    # Read from db and return the value
    # This is basically for the timeout of checking the retries
    # Temporarily returning 10 seconds
    return 10

def unblocking(lock):
    # Reads the force_remove value of the IP table
    # If its true: remove the entry from the system IPTable
    # If not do nothing
    print "Unblocking the ip addr..!!"
    lock.acquire()
    for ip in iptable.keys():
        if iptable[ip][3] == True:
            # 1. Remove the entry from DB
            # 2. Remove the entry from the system IP table
            iptable.pop(ip)
            import subprocess
            # Make sure that allowBlock.sh is in the same directory as this script
            # And also PATH variable is exported with current working directory appended to the PATH
            subprocess.call(["allowBlock.sh", ip, "ALLOW"])
    lock.release()

def consumer(lock):
    print "Consumer..!!"
    # 1. Validates the

def producer(ipaddr, lock):
    print "Producer..!!"
    # Read from the configuration file
    # Get the thresholds
    # Validate against the current ip address
    timeV = time.clock()
    lock.acquire()
    if iptable.has_key(ipaddr):
        print "Key found"
        startTime = iptable[ipaddr][0]
        tCount = iptable[ipaddr][1]
        # Assumption: When there is block start, then there wont be any new
        #             requests coming for the ip address
        if iptable[ipaddr][3] == False:
            if startTime + getThTimeTicks() <= timeV:
                iptable[ipaddr] = [timeV, 1, 0, False]
            else:
                iptable[ipaddr] = [startTime, tCount+1, None, False]
        else:
            # Do nothing, reason the unblock thread will try to clean
            # We dont need to worry about the race conditino
            print "Unblock thread should have to take care of this ip ", ipaddr
    else:
        # No entry present in the table
        # Adding an entry to the table
        iptable[ipaddr] = [timeV, 1, None, False]
    lock.release()

def getIPAddr();
    # Read the log file
    # Find the pattern
    # Get the IP address
    # Return it as a string
    for ip in iplist:
        yield ip

# Managing Threads using this class
class ThreadLibrary(threading.Thread):
    def __init__(self, func, *args, **kwargs):
        threading.Thread.__init__(self)
        self.args = args
        self.func = func
        self.kwargs = kwargs
        self.runnable = True

    def run(self):
        while self.runnable:
            self.func(*self.args, **self.kwargs)
            time.sleep(5)

    def stop(self):
        self.runnable = False

if __name__ == "__main__":
    print "Application Started.!"
    # Read the file indefinitely - log

    for ipaddr in getIPAddr():
        lock = threading.RLock()
        t1 = ThreadLibrary(producer, ipaddr, lock)
        t2 = ThreadLibrary(consumer, ipaddr, lock)
        t3 = ThreadLibrary(unblocking, ipaddr, lock)

        # 1. Run Producer Thread
        # 2. Run Consumer Thread
        # 3. Run Unblock Thread
        t1.start()
        t2.start()
        t3.start()

    print "Application Exitted.!"