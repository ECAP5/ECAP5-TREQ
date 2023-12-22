from ecap5_treq.log import log_imp, log_warn, log_error

def test_log_imp():
   # The log shall be empty at startup 
   assert len(log_imp.msgs) == 0

   for i in range(10):
       log_imp("{}".format(i))

   # Check the number of logged messages
   assert len(log_imp.msgs) == 10
   # Check the logged messages
   for i in range(10):
       assert log_imp.msgs[i] == "{}".format(i)

def test_log_warn():
   # The log shall be empty at startup 
   assert len(log_warn.msgs) == 0

   for i in range(10):
       log_warn("{}".format(i))

   # Check the number of logged messages
   assert len(log_warn.msgs) == 10
   # Check the logged messages
   for i in range(10):
       assert log_warn.msgs[i] == "{}".format(i)

def test_log_error():
   # The log shall be empty at startup 
   assert len(log_error.msgs) == 0

   for i in range(10):
       log_error("{}".format(i))

   # Check the number of logged messages
   assert len(log_error.msgs) == 10
   # Check the logged messages
   for i in range(10):
       assert log_error.msgs[i] == "{}".format(i)
