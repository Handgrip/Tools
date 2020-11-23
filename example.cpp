// discard
#include <bits/stdc++.h>
#include <unistd.h>
using namespace std;
char tmps[1000005];
int nex[1005];

inline int kmp(const string &a, const string &b, int s = 0) {
    int n = a.length();
    int m = b.length();
    {
        nex[0] = -1;
        int j = 0, k = -1;
        while (j < m) {
            if (k == -1 || b[j] == b[k]) {
                nex[++j] = ++k;
            } else {
                k = nex[k];
            }
        }
    }
    {
        int i = s, j = 0;
        while (i < n && j < m) {
            if (j == -1 || a[i] == b[j]) {
                i++, j++;
            } else {
                j = nex[j];
            }
        }
        if (j == m) {
            return i - j;
        } else {
            return -1;
        }
    }
}
inline bool sys(const string &cmd) {
    return system((cmd + " >/dev/null 2>&1").c_str());
}
inline bool sysget(string &res, const string &cmd, int maxline = 1000) {
    static FILE *in;
    res.clear();
    in = popen(cmd.c_str(), "r");
    if (!in)
        return false;
    int linecnt = 0;
    while (linecnt++ < maxline && fgets(tmps, 100005, in)) {
        res += tmps;
    }
    pclose(in);
    return true;
}
inline int getcpu(void) {
    static string res;
    sysget(res, R"(top -bn 1 |grep Cpu | cut -d "." -f 1 | cut -d ":" -f 2)");
    return stoi(res);
}

int main(void) {
    return 0;
}