CALLER_FILEPATH=$1
SHOULD_DELETE=$2

CMD="import rpyc, sys; c = rpyc.connect(\"localhost\", 12345).root; print(c.processVsCodeCall('$CALLER_FILEPATH', '$SHOULD_DELETE'), file=sys.stdout)"
python -c "$CMD"