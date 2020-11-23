ps -fe|grep wssh |grep -v grep
if [ $? -ne 0 ];then
    echo start process......
    nohup /usr/local/bin/wssh --address='127.0.0.1' --port=7000 >>/home/wwwlogs/wssh.log 2>&1 &
else
    echo runing......
fi