import numpy as np

tOld=1.5
t0=1
tmax=5
X = (tOld - t0) / (tmax - t0)
print(X)

fshape_test = 1.5
print(np.power(X, 1 / fshape_test))