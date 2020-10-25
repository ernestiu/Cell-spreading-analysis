'''
find_relevant_max extracts the relevant maximas

                           
'''
import numpy as np
def find_relevant_max(i_max, val_max, i_min, val_min, REL_RELEVANCE = 0.05, TOT_RELEVANCE = 0.005):
    
    #find the absolute maximum
    total_max = np.max(val_max)
    #i_total_max = val_max.index(max(val_max))
    
    index = 0
    rel_max_ind = np.empty((1,0), dtype=np.int64)
    rel_max_val = np.empty((1,0), dtype=np.float64) 
    rel_min_ind = np.empty((1,0), dtype=np.int64)
    rel_min_val = np.empty((1,0), dtype=np.float64)
    store_last = False

    while len(val_max) > 1 and not store_last:
        #find the temporary absolute maximum
        #max_0 = max(val_max)
        i_0 = np.argmax(val_max)
        i_m = 0
        #check if there is a minima to the right
        right_min = True #1
        left_min = False #0
        while i_m <= (len(i_min)-1) and i_min[i_m] < i_max[i_0]:
            i_m = i_m + 1
            
        if i_m > (len(i_min)-1):
            left_min = True
            right_min = False
            i_m = (len(i_min)-1)
            while i_m >= 0 and i_min[i_m] > i_max[i_0]:
                i_m = i_m - 1
            if i_m < 0:
                left_min = False
               
  #calculate the significance
        d_1 = (val_max[i_0]-val_min[i_m])/val_max[i_0]
        rel_relevance = d_1
        if index > 0:
            total_relevance = val_max[i_0]/total_max
        else:
            total_relevance = 1
                    
 # if relevant, store in significant_list and delete from val_max list
        
        if rel_relevance > REL_RELEVANCE and total_relevance > TOT_RELEVANCE:
            #store relevant index
             
            #rel_max_ind[index] = i_max[i_0]
            rel_max_ind = np.append(rel_max_ind, i_max[i_0])
            #store relevant's index value
            
            #rel_max_val[index] = val_max[i_0]
            rel_max_val = np.append(rel_max_val, val_max[i_0]) #line 98
            
            if not store_last:# 
            
               rel_min_ind = np.append(rel_min_ind, i_min[i_m])
                #rel_min_ind = [i_min[i_m]]
                
               rel_min_val = np.append(rel_min_val, val_min[i_m])
                #rel_min_val = [val_min[i_m]]
            index = index + 1
            #delete relevant maxima and minima
            val_max = np.delete(val_max, i_0)
            i_max = np.delete(i_max, i_0)

            if len(val_min) == 1:
              store_last = True
              #last_val_min = val_min[0]
              #last_i_min = i_min[0]
        
            if not store_last:
                val_min = np.delete(val_min, i_m)
                i_min = np.delete(i_min, i_m)

        
        elif not (rel_relevance > REL_RELEVANCE and total_relevance > TOT_RELEVANCE):
          #delete non-relevant minima and maxima
          if right_min and len(val_max) >= i_0 + 2:
              val_max = np.delete(val_max, i_0+1)
              i_max = np.delete(i_max, i_0+1)

        
          elif left_min and i_0 >= 1: 
              val_max = np.delete(val_max, i_0-1)
              i_max = np.delete(i_max, i_0-1)

        
          elif len(val_max) > 1: #new an maybe wrong
              val_max = np.delete(val_max, i_0)
              i_max = np.delete(i_max, i_0)

            
          if len(val_min) > 1: #new
              val_min = np.delete(val_min, i_m)
              i_min = np.delete(i_min, i_m)

    #check the remaining extremas
    if len(val_min) == 1:
        
        d_1 = (val_max[0] - val_min[0])/val_max[0]
        rel_relevance = d_1
        total_relevance = val_max[0]/total_max
        if rel_relevance > REL_RELEVANCE and total_relevance > TOT_RELEVANCE:
            if index > (len(rel_max_ind)-1):
                rel_max_ind = np.append(rel_max_ind, i_max[0])
                rel_max_val = np.append(rel_max_val, val_max[0])
            else:
                rel_max_ind[index] = i_max[0]
                rel_max_val[index] = val_max[0]
            if index > (len(rel_min_ind)-1):
                rel_min_ind = np.append(rel_min_ind, i_min[0])
                rel_min_val = np.append(rel_min_val, val_min[0])
            else:
                rel_min_ind[index] = i_min[0]       
                rel_min_val[index] = val_min[0]
            index = index + 1
    else:
        #if there is no minima for comparison take only absolute
        total_relevance = val_max[0]/total_max
        if total_relevance > TOT_RELEVANCE:
            #store relevant index
            rel_max_ind[index] = i_max[0] #original code 
            #rel_max_ind = [i_max[0]]
            
            rel_max_val[index] = val_max[0] #original code   
            #rel_max_val = [val_max[0]]
            
            index = index + 1
#check the last maxima against the total maxima
#this has to be done because there might be no minima left which is enough low. 
    if len(val_max) == 1:
        total_relevance = val_max[0]/total_max
        if total_relevance > TOT_RELEVANCE:
            if index < (len(rel_max_ind)-1):
                rel_max_ind[index] = i_max[0]
            else:
                rel_max_ind = np.append(rel_max_ind, i_max[0])
            if index < (len(rel_max_val)-1):
                rel_max_val[index] = val_max[0]
            else:
                rel_max_val = np.append(rel_max_val, val_max[0])
    
    #now find the two main maximas
    #first_max = max(rel_max_val)
    i_first_max = np.argmax(rel_max_val)
    ind_max = np.empty((1,0), dtype=np.int64)
    ind_max = np.append(ind_max, rel_max_ind[i_first_max])

    rel_max_val = np.delete(rel_max_val, i_first_max)
    rel_max_ind = np.delete(rel_max_ind, i_first_max)
   
    #found = 0
    while len(rel_max_val) > 0:
        #second_max = max(rel_max_val)
        i_second_max = np.argmax(rel_max_val)
        if len(ind_max) > 1:
            ind_max[1] = rel_max_ind[i_second_max]
        else: 
            ind_max = np.append(ind_max, rel_max_ind[i_second_max])
        rel_max_val = np.delete(rel_max_val, i_second_max)
        rel_max_ind = np.delete(rel_max_ind, i_second_max)
 
        #now find the minima between these two maximas
        ind_max = np.sort(ind_max)

        for i in range(len(rel_min_ind)-1):
            if rel_min_ind[i] > ind_max[0] and rel_min_ind[i] < ind_max[1]:
                #found = 1
                ind_min = [rel_min_ind[i]]
                return ind_max, ind_min

    try:
        ind_min
    except NameError:
        ind_min_EXIST = False
    else:
        ind_min_EXIST = True
        
    try:
        ind_max
    except NameError:
        ind_max_EXIST = False
    else:
        ind_max_EXIST = True    
        
           
    if ind_min_EXIST == False or ind_max_EXIST == False:
        ind_max = np.array([-99])
        ind_min = np.array([-99])
        return ind_max, ind_min

    




