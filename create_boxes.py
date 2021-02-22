import random
import math

heights = [random.randint(1, 20) for x in range(10)]
lengths = [random.randint(1, 20) for x in range(10)]
area = [lengths[x] * heights[x] for x in range(10)]
area_sum = sum(area)
bin_size = math.sqrt(area_sum)
for box in range(len(area)):
   heights[box] = heights[box] * 1000/bin_size
   lengths[box] = lengths[box] * 1000/bin_size
   area[box]= area[box] * 1000/Total

box = 0
boxes = []
row_height = random.randint(1, 6)
residual = bin_size
while box < 10 :
   scaled_length = area[box]/row_height
   if scaled_length <= residual:
      boxes.append((row_height, scaled_length))
      residual = residual - scaled_length
      box += 1
   else :
      boxes.append((row_height, residual))
      area[box] = area[box] - (row_height * residual)
      row_ht = random.randint(1, 6)
      residual = bin_size