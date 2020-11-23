echo stopping......
autossh_id=`ps -ef | grep -E autossh | grep -v grep | awk '{print $2}'`
echo $autossh_id
for id in $autossh_id
do
    kill $id
    echo killed $id
done
echo start process......
autossh -M 4010 -fNCR  12345:localhost:80 -p 22 root@100.100.100.100