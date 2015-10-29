
import sys, time
import threading

# Key: IP address
# Value: [start_time, count, block_start, force_remove]
# force_remove: is for those IP addresses which are unblocked by the admin
#               which is basically removing the IP Table entry
iptable={}

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

def unblocking():
    # Reads the force_remove value of the IP table
    # If its true: remove the entry from the system IPTable
    # If not do nothing
    print "Unblocking the ip addr..!!"
    lock = threading.RLock()
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

def consumer():
    print "Consumer..!!"

def producer(ipaddr):
    print "Producer..!!"
    # Read from the configuration file
    # Get the thresholds
    # Validate against the current ip address
    timeV = time.clock()
    lock = threading.RLock()
    lock.acquire()
    if iptable.has_key(ipaddr):
        print "Key found"
        startTime = iptable[ipaddr][0]
        tCount = iptable[ipaddr][1]
    else:
        # No entry present in the table
        # Adding an entry to the table
        iptable[ipaddr] = [timeV, 1, 0, False]
    lock.release()


if __name__ == "__main__":
    print "Application Started.!"
    line =
    # Read the log file
    #