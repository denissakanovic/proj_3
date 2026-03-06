# Denis Sakanovic
# microLSP evaluation model

def LARGE(value: int, min_: int, max_: int) -> int:

  # we want to compare the value
  if value <= min_:
    return 0
  
  elif value >= max_:
    return 1

  else:
    # value lives in between min & max
    # 0 -> not acceptable
    # 1 -> best
    # so, [min_, max_] -> [0, 1]
    # we want min_ to be 0
    return round((value - min_) / (max_ - min_), 2)

def SMALL(value: int, min_: int, max_: int) -> int:

  if value <= min_:
    return 1
  
  elif value >= max_:
    return 0

  else:
    # we want [min_, max_] -> [1, 0]
    # so,
    return round((max_ - value) / (max_ - min_), 2)

# too small OR too large is bad
def RANGE(value: int, min_: int, range_min: int, max_: int, range_max: int) -> int:

  if value >= range_min and value <= range_max:
    return 1
  
  elif value <= min_ or value >= max_:
    return 0

  elif value < range_min:
    return (value - min_) / (range_min - min_)
  
  else:
    # handles vals between range_max and max_
    return (max_ - value) / (max_ - range_max)

# clamp helper just to keep values between 0 and 1
def clamp01(x: float) -> float:
  return max(0.0, min(1.0, x))

def wpm(x, w, r):

  # catch some logic errors that would break our program
  if len(x) != len(w): raise ValueError("x and w must be same length")
  if abs(sum(w) - 1) > 1e-9: raise ValueError("weights must sum to 1")

  total = 0.0
  for xi, wi in zip(x, w): # we are zipping x and w together to get (x, w) 
    xi = clamp01(xi)
    if r < 0 and xi == 0: return 0.0
    total += wi * (xi ** r) # summation: going to n, when i = 1, for wixi^r
  return clamp01(total ** (1/r)) # sum^1/r

# price preference 
def price_pref(C, Cmin, Cmax):
  return clamp01((Cmax - C) / (Cmax - Cmin))

# conjunction: use conjunctive WPM (r = -1) with equal weights
def conj(a, b):
  return wpm([a, b], [0.5, 0.5], r=-1)

# computes overall suitability X  
def suitability_X(ssd_gb, ram_gb, battery_hr, weight_lb, camera_mp):
  # convert raw values to preference scores
  ssd = LARGE(ssd_gb, 128, 512)
  ram = LARGE(ram_gb, 4, 16)
  battery = LARGE(battery_hr, 4, 8)
  weight = SMALL(weight_lb, 2.5, 6)
  camera = LARGE(camera_mp, 1, 1.3)

  # RAM matters slightly more than SSD
  performance = wpm([ram, ssd],         [0.6, 0.4], r=-1) # RAM, SSD
  # weight matters slightly more than battery
  portability = wpm([weight, battery],  [0.6, 0.4], r=-1) # Weight, Battery

  # allows tradeoffs between performance, portability, and camera
  X = wpm([performance, portability, camera], [0.45, 0.45, 0.10], r=1)  # GCD
  return X

if __name__ == "__main__":

  """
  Inputs: SSD, RAM, Camera, Weight, and Batter Life
  Vertex Notation:

  Crit(SSD [GB])            = { (128,0), (512,100) }
  Crit(RAM [GB])            = { (4,0), (16,100) }
  Crit(Battery Life [hr])   = { (4,0), (8,100) }
  Crit(Weight [lb])         = { (2.5,100), (6,0) }     
  Crit(Camera [MP])         = { (1,0), (1.3,100) }

  /Attribute Roles:/
  SSD (GB): storage capacity ;) More storage makes life easier.
  RAM (GB): more RAM reduces slowdowns in development workflows. 
  Battery life (hr): it's better to have longer battery life than not. Also, I tend to program in the woods, and there are no outlets in the woods.
  Weight (lb): portability/comfort carrying to class.
  Camera (MP): better webcam quality so that my Mom can see my face clearer when I move to Europe and never come back


                            /Suitability aggregation tree:/

                           GCD  (Overall Suitability)  (WPM, r = 1)
                          /            |               \ 
                         /             |                \     
        Performance (WPM, r = -1)   Portability (WPM, r = -1)   Camera (leaf)
             /        \                /         \
            /          \              /           \
         RAM          SSD          Weight        Battery

  """
          
  dell = [[512, 256, 512], [16, 8, 8], [12, 6, 14], [3.2, 3.0, 2.7], [1.2, 1.1, 1.3], [1200, 800, 1100]]  
  hp = [[512, 256, 1024], [16, 8, 16], [10, 8, 12], [2.9, 3.3, 3.0], [1.3, 1.0, 1.2], [1300, 900, 1400]]
  
  dell_laptops = []
  hp_laptops = []
  Cmin = 900 # ideal 
  Cmax = 2000  # unacceptable

  # build dell laptops
  for j in range(len(dell[0])):
    curr = []
    for i in range(len(dell)): 
      curr.append(dell[i][j])
    dell_laptops.append(curr)


  # build hp laptops
  for j in range(len(hp[0])):
    curr = []
    for i in range(len(hp)):
      curr.append(hp[i][j])
    hp_laptops.append(curr)

  # evaluate dell laptops
  for laptop in dell_laptops:
    ssd_gb, ram_gb, battery_hr, weight_lb, camera_mp, C = laptop

    X = suitability_X(ssd_gb, ram_gb, battery_hr, weight_lb, camera_mp)
    Pc = price_pref(C, Cmin, Cmax)
    V = conj(X, Pc)

    print(f"Dell Laptop: {laptop}")
    print(f"X (suitability): {round(X, 2)}")
    print(f"Pc (price pref): {round(Pc, 2)}")
    print(f"V (overall value): {round(V, 2)}")
    print()

  # evaluate hp laptops
  for laptop in hp_laptops:
    ssd_gb, ram_gb, battery_hr, weight_lb, camera_mp, C = laptop

    X = suitability_X(ssd_gb, ram_gb, battery_hr, weight_lb, camera_mp)
    Pc = price_pref(C, Cmin, Cmax)

    V = conj(X, Pc)

    print(f"HP Laptop: {laptop}")
    print(f"X (suitability): {round(X, 2)}")
    print(f"Pc (price pref): {round(Pc, 2)}")
    print(f"V (overall value): {round(V, 2)}")
    print()


