import time
from isochrones import get_ichrone
mist = get_ichrone('mist', bands=['J'])

mist.radius(1, 9.5, 0.1)

N = 10000

start = time.time()
for i in range(N):
    mist.radius(1, 9.6, 0.01)
end = time.time()

print('Time per isochrones execution: {}s'.format((end-start)/N))

