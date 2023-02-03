import rpyc 
c = rpyc.connect("localhost", 12345).root 
c.processLink("1", "2", "3", "4")
        