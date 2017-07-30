def sync_images_buckets(stream1, stream2, timestamp_interval):
  ## bucketize time and get one image within each bucket
  output_images1 = []
  output_images2 = []
  
  p1 = 0
  p2 = 0
  max_length = len(stream1) if len(stream1) > len(stream2) else len(stream2)
  while p1 < max_length and p2 < max_length:
    item1 = stream1[p1]
    item2 = stream2[p2]
    timestamp1 = item1[0]
    timestamp2 = item2[0]
    
    if timestamp1 < timestamp2:  
      if abs(timestamp2-timestamp1) <= timestamp_interval:
        nearest = (item1, abs(timestamp2-timestamp1), p1)

        p1_temp = p1 + 1
        item1_temp = stream1[p1_temp]
        timestamp1_temp = item1_temp[0]
        
        # Try to find nearer timepoint
        while abs(timestamp2-timestamp1_temp) <= timestamp_interval:
          if abs(timestamp2-timestamp1_temp) < nearest[1]:
            nearest = (item1_temp, abs(timestamp2-timestamp1_temp, p1_temp))
          p1_temp += 1    
          item1_temp = stream1[p1_temp]
          timestamp1_temp = item1_temp[0]
        
        output_images1.append(nearest[0][1])
        output_images2.append(item2[1]) 
        p1 = p1_temp + 1 
      else:
        p1 += 1
    else:
      if abs(timestamp1-timestamp2) <= timestamp_interval:
        nearest = (item2, abs(timestamp1-timestamp2))
      else:
        p2 += 1
        
        
        
        
  '''
  item1 = stream1.pop(0)
  item2 = stream2.pop(0)
  timestamp1 = item1[0]
  timestamp2 = item2[0]

  if timestamp1 < timestamp2: # Compare timestamps
    nearest = (item1, abs(timestamp2-timestamp1))
    while abs(timestamp2-timestamp1) < timestamp_interval:
      item1 = stream1.pop(0)
      timestamp1 = item1[0]
      if abs(timestamp2-timestamp1) < nearest[1]:
        nearest = (item1, abs(timestamp2-timestamp1))
         
  '''
  
  return output_images1, output_images2
