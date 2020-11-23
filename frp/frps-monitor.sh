#!/bin/sh
curl localhost:12345 --connect-timeout 1 -m 1
if [ $? == 0 ]; then
    echo ok, available
else
    ps -ef | grep 'sshd: root' | grep -v grep | grep -v @pts
    if [ $? -ne 0 ];then
        echo stopped......
    else
        echo stopping......
        ssh_id=`ps -ef | grep 'sshd: root' | grep -v grep | grep -v @pts | awk '{print $2}'`
        echo $ssh_id
        for id in $ssh_id
        do
            kill $id
            echo killed $id
        done
    fi
fi