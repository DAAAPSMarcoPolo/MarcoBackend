import psutil

# For testing purposes only
p = psutil.Process(13947)
p.terminate()