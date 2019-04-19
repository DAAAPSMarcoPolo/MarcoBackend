import psutil

# For testing purposes only
p = psutil.Process(7958)
p.terminate()