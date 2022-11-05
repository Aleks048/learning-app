def autolog(message):
    "Automatically log the current function details."
    import inspect, logging
    # Get the previous frame in the stack, otherwise it would
    # be this function!!!
    # logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    func = inspect.currentframe().f_back.f_code
    # Dump the message + the name of this function to the log.
    logging.warning("\n%s: [%s] in %s:%i\n" % (
        message, 
        func.co_name, 
        func.co_filename, 
        func.co_firstlineno
    ))