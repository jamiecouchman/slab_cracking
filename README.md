# slab_cracking
A script that iteratively cracks a slab and redistributes moments in GSA

Inputs should be written directly into the inputs.txt file, all you need to use the script is:

  1. A GSA slab model, with it's directory to hand
  2. A governing load case, typically ULS Envelope to get the maximum sagging and hogging moments
  3. Put the 2D slab elements into a GSA list, then provide the list number
  4. An Adsec section of the slab, from the Moment/Stiffness graph you can determine the cracking moment at which the slab cracks and loses stiffness.
  5. From the Adsec section you can then work out what proportion of the stiffness is lost and assign a new 'cracked' section property in GSA. Provide property numbers for both     uncracked and cracked sections

The script works by:

  1. Analysing the model
  2. Going through every slab element (in the assigned list) and checking if the maximum or minimum moment is above the cracking moment. If it is it puts the element into a 'cracked_elements' dictionary
  3. Results are deleted.
  4. It then iterates through this dictionary and changes the property of each element to the cracked property.
  5. If the number of iterations exceeds the maximum, or there are no elements in 'cracked elements' the iteration stops, if not it repeats the process with new properties, re-distributing moments
  6. This should ensure that the correct elements are cracked and the deflections are accurate, and less conservative than cracking every element.
