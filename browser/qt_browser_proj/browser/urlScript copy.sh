cmd="import rpyc, sys;
c = rpyc.connect(\"localhost\", 12345).root;
data:map = c.processBrowserCall('${1}');
for k,v in data.items():
    v_str = '::::'.join([str(i) for i in v])
    k = str(k)
    k = str(k).replace('https://localhost/', '')
    k = str(k).replace('http://localhost/wiki/A/', 'wiki/')
    print(v_str + '::::' + k, file=sys.stdout);
#print(c.processBrowserCall('${1}'), file=sys.stdout);
"
/Users/ashum048/books/_python_local/3.9.18/bin/python3.9 -c "${cmd}"
