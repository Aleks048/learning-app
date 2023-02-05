CALLER_MAIN_TEX_FILEPATH=$1

CMD="import rpyc; c = rpyc.connect(\"localhost\", 12345).root; c.processSaveTexFile('${CALLER_MAIN_TEX_FILEPATH}')"
echo "Running command: "$CMD
python3 -c "$CMD"