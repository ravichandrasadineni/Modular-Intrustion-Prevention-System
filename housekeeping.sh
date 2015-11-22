for i in `ps -ef| grep -i Intrusion| grep -v 'grep' |awk -F" " '{print $2}'`
do
	sudo kill -9 $i
done
