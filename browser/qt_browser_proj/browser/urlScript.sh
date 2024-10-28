cmd="import rpyc, sys;
c = rpyc.connect(\"localhost\", 12345).root;
response = c.processBrowserCall('''${1}''');
if response != None:
    data:map = dict(response);
    if data != None:
        if type(data) == dict:
            for k,v in data.items():
                try:
                    v = dict(v)
                except:
                    continue
                v_str = ''
                for vk, vv in v.items():
                    v_str += vk + '////' + vv + '::::'
                    v_str = v_str.replace('\n', '')
                k = str(k)
                k = str(k).replace('https://localhost/', '')
                k = str(k).replace('http://localhost/wiki/A/', 'wiki/')
                print(v_str + k, file=sys.stdout);
"
/Users/ashum048/books/_python_local/3.9.18/bin/python3.9 -c "${cmd}"
