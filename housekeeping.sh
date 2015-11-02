for i in `ps -ef| grep -i Intrusion| grep -v 'grep' |awk -F" " '{print $2}'`
do
	kill -9 $i
done
