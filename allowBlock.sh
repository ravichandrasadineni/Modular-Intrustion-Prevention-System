#!/bin/bash
#
# Works only on Linux machines
# Arg1: IP Address 
# Arg2: DROP/ALLOW
#   

IPTADDCMD="/sbin/iptables -I INPUT -s "
IPTAPPCMD="/sbin/iptables -A INPUT -s "
IPTDRPCMD="/sbin/iptables -D INPUT -s "
# LOG1="/var/log/auth.log"
# LOG2="/var/log/apache2/access.log"

# Reading the command line arguments
IPADDR=$1
OPTION=$2

# Functions

# Usage of the utility
Usage() {
	echo "allowBlock.sh <IP Address> <OPTION>"
	echo
	echo "DESCRIPTION"
	echo "    Administration tool for allowing/dropping the packets from an IP Address"
	echo "    IP Address: IP Address to manage"
	echo "    OPTION: ALLOW/DROP"
	echo "          ALLOW:"
	echo "               Enables the packet processsing from the given IP Address"
	echo "          DROP:"
	echo "               Disbles the packet processsing from the given IP Address"
	exit 0
}

# CLI validation
if [ $# -ne 2 ]
then
	Usage
fi

# Allowing / Dropping administration using iptables utility
if [ "$2" == "DROP" ]
then
        eval ${IPTADDCMD}${IPADDR}" -j DROP"
elif [ "$2" == "ALLOW" ]
then
        eval ${IPTDRPCMD}${IPADDR}" -j DROP"
fi

# Monitoring the Log files
# if [-f $LOG1]
# then
	# Perform the Auth Log parsing
	# Check for any issues with logging
	# Block the IPs accordingly
	
# fi