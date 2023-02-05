#!/bin/bash
URL=$1
cmd="import rpyc; c = rpyc.connect(\"localhost\", 12345).root; c.processLink('${URL}')"
python3 -c "${cmd}"