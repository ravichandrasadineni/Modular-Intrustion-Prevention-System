import ipTableManager
import sys, time
import threading
import subprocess
# Key: IP address
# Value: [start_time, count, block_start, force_remove]
# force_remove: is for those IP addresses which are unblocked by the admin
#               which is basically removing the IP Table entry
iptable={}

# iplist = ["1.2.3.4", "1.2.3.5", "1.2.3.6", "1.2.3.7", "1.2.3.8"]
lock = threading.RLock()
fullCondition = threading.Condition(lock)
queue = []

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
                print "[Consumer] Successfully unblocked: ", ip[0]
            except:
                print "[Consumer] Unblocking of ", str(ip[0]), " failed.!"
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
            ipaddr = queue.pop(0)
            print "Consuming..!! IP: ", ipaddr
            if ipTableManager.process_new_ip(ipaddr) == True:
                # Block the IP
                try:
                    subprocess.call(["./allowBlock.sh", ipaddr, "DROP"])
                    print "[Consumer] Successfully blocked: ", ipaddr
                except:
                    print "**** [Consumer] Blocking ", ipaddr, " Failed ", sys.exc_info()[0]
            fullCondition.notify()
            fullCondition.release()
            # time.sleep(1)
        print "Consumer End..!! IP: ", ipaddr

class Producer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # self.queue = queue
        # self.fullCondition = condition

    def run(self):
        # Read the log file
        # Find the pattern
        # Get the IP address
        # Return it as a string
        # Logic to read the log files and update the ip
        # So that the producer will make an entry to the table
        # fileDesc = open("/var/adm/log/auth.log", "r")
        global fullCondition, queue, lock
        fileDesc = open("./auth.log", "r")
        fileDesc.seek(0,2)
        while True:
            # print "In producer"
            fullCondition.acquire()
            if len(queue) >= 1:
                # Assuming queue is full
                print "In cond wait of producer.!"
                fullCondition.wait()
            ip = fileDesc.readline().strip()
            if not ip:
                time.sleep(0.1)
                continue
            else:
                # Need to add more logic to get only the IP Address
                queue.append(ip)
            print "Producing: ", ip, " Queue ", queue
            fullCondition.notify()
            # print "Notifying the consumer.."
            fullCondition.release()
            # print "Released..!!!"
            # time.sleep(5)

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

    Producer().start()
    Consumer().start()
    ublock_thread = threading.Thread(target=unblocking)
    ublock_thread.start()
    print "Application Exitted.!"