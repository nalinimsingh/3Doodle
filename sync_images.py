def sync_images_buckets(stream1, stream2, timestamp_interval):
  ## bucketize time and get one image within each bucket
  output_images1 = []
  output_images2 = []
  
  # anchor = max(stream1[0][0], stream2[0][0])
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
        
    
  
  return output_images1, output_images2
