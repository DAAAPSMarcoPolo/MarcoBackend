import psutil

# For testing purposes only
p = psutil.Process(23373)
p.terminate()