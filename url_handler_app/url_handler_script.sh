URL=$1
# TT="/Users/ashum048/books/test.txt"
cmd="import rpyc; c = rpyc.connect(\"localhost\", 12345).root; c.processLink('${URL}')"
/opt/homebrew/bin/python3 -c "${cmd}" 
# &>${TT}