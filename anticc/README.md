# anticc

anticc 检测单个 ip 的连接数，若连接数过大，则通过 iptables/ipset 封禁该 ip。

基于<https://github.com/Roslandas/MANAGER/tree/master/DDOS> 进行 py 重构，同时消除原有 bug。

适用于 Ubuntu。
