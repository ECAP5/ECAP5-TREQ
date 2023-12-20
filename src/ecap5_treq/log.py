import sys

def log_imp(msg):
    print("IMPORTANT:", msg, file=sys.stderr)
    log_imp.msgs += [msg]
log_imp.msgs = []

def log_warn(msg):
    print("WARN:", msg, file=sys.stderr)
    log_warn.msgs += [msg]
log_warn.msgs = []

def log_error(msg):
    print("ERROR:", msg, file=sys.stderr)
    log_error.msgs += [msg]
log_error.msgs = []
