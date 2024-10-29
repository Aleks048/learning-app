URL=$1
# TT="/Users/ashum048/books/test.txt"
cmd="import rpyc, sys; c = rpyc.connect(\"localhost\", 12345).root; c.processLink('${URL}')"
/Users/ashum048/books/_python_local/3.9.18/bin/python3.9 -c "${cmd}"
# &>${TT}