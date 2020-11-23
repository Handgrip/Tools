#!/bin/sh
ping 114.114.114.114 -c 1
if [ $? == 0 ]; then
    ps -fe|grep autossh |grep -v grep
    if [ $? -ne 0 ];then
        echo start process......
        autossh -M 4010 -fNCR  12345:localhost:80 -p 22 root@100.100.100.100
    else
        echo runing......
    fi
else
    ps -ef | grep -E autossh | grep -v grep
    if [ $? -ne 0 ];then
        echo stopped......
    else
        echo stopping......
        autossh_id=`ps -ef | grep -E autossh | grep -v grep | awk '{print $2}'`
        echo $autossh_id
        for id in $autossh_id
        do
            kill $id
            echo killed $id
        done
    fi
fi