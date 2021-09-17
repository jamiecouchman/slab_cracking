#import gsapy module
import gsapy
from gsapy import Node, Element, GSA, GSAError
from gsapy.output_dataref import Output_DataRef as dr
from configparser import ConfigParser


config = ConfigParser()
config.read("inputs.txt")


#load a model file
dir = config['model']['dir']
file = config['model']['file']
path = "\\".join([dir,file])
model = GSA(path, version="10.1")

#INPUTS
governing_load_case_max = config['inputs']['governing_load_case']+'max'     #ULS load case governing, use max if envelope case  
governing_load_case_min = config['inputs']['governing_load_case']+'min'     #ULS load case governing, use max if envelope case 
M_cracking = float(config['inputs']['M_cracking'])       #design tensile strength of concrete
max_iterations = int(config['inputs']['max_iterations'])      #Maximum iterations to crack - run time per iteration approx 130s          
slab_elements_list_no = int(config['inputs']['slab_elements_list_no']) #GSA list number that contains stability elements
prop1 = int(config['inputs']['prop1'])       #2D element property for first wall thickness       
prop1_cracked = int(config['inputs']['prop1_cracked'])       #2D element property for cracked first wall thickness  

def get_2D_elem_forces_DRV(index, case, axis='default', averaged: bool = False):
    '''
    :param index: 2D element index or iterator of indices
    :param case: A string describing the case for which you want to extract results.
    :param axis: either 'global', 'local', 'default' or the number of a user defined axis, axis with respect to
                 which results should be extracted.
    :param averaged: averaged: whether or not results should be averaged.
    :return: tuple of forces [MMAX, MMIN, MANG, NMAX, NMIN]
    '''
    try:
        return [model.get_2D_elem_forces(i, case, axis, averaged) for i in index]
    except TypeError:
        results_full = model._get_2D_elem_results(index, 0, axis, case, dr.REF_FORCE_EL2D_DRV, averaged)
        return_indices = range(2, 7)
        return [tuple(result[ri] for ri in return_indices) for result in results_full]   
    

try:
    from time import time
    t=[time()]
    tension = True
    i=0
    no_tension_elements=[]
    
    while tension == True:
        i+=1
        if i > max_iterations:
            break
        
        print('beginning iteration:',i)
        #analyse model
        print('starting first analysis task')
        model.analyse(1)
        model.analyse(2)
        
        GSA_lists = model.get_all_saved_lists() #ensure you hav eno empty lists
        slab_elements = model._get_entities_in_numbered_list(slab_elements_list_no)
        cracked_elements = {}
        
        print('assembling cracked dictionary\n')
        #find which elements are above conrete uncracked moment capacity
        
        for element in slab_elements:
            M_tup_max = get_2D_elem_forces_DRV(element, governing_load_case_max)
            M_max=M_tup_max[0][0]
            M_tup_min = get_2D_elem_forces_DRV(element, governing_load_case_min)
            M_min=M_tup_min[0][1]
            
            if M_max >= M_cracking:
                cracked_elements[element]=M_max
            elif M_min <= -M_cracking:
                cracked_elements[element]=M_min
                
                
        print('There are',len(cracked_elements),'elements exceeding cracked Moment')
#        print('cracked elements are',cracked_elements)
        maxmoment = max(cracked_elements.items(), key=lambda k: k[1])
        print('maximum moment in element',maxmoment[0],'with value of',maxmoment[1])
        minmoment = min(cracked_elements.items(), key=lambda k: k[1])
        print('minimum moment in element',minmoment[0],'with value of',minmoment[1])
        no_tension_elements.append(len(cracked_elements))
                
        if len(cracked_elements) > 0:
            tension=True
            print('cracking elements')
            #delete results
            model.gsa.delete('RESULTS')
            
            #change properties to 'cracked'
            for key in cracked_elements:        
                element=model.get_elements(key)
                if element.prop == prop1:                    
                    element.prop=prop1_cracked
                model.set(element)
                element=model.get_elements(key)
        
        else:
            tension=False  
        
        #model.save()
        t.append(time())
        print('iteration completed in time of',t[i]-t[i-1],'seconds\n')
        
    #save the model 
    newfile = config['model']['new_file']
    newpath = "\\".join([dir,newfile])
    model.save_as(newpath)  
    print('iterations completed and new model saved')

# close the model
finally:
    model.close()