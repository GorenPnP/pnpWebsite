import multiprocessing

accesslog = "-"     # log to std.out
errorlog = "-"      # log to std.err
loglevel = "info"   # can be one of ['debug','info','warning','error','critical']

workers = multiprocessing.cpu_count() * 2 + 1
