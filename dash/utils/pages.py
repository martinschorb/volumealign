#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 14:24:32 2020

@author: schorb
"""

import params
import dash_core_components as dcc


def init_store(storeinit,module):
    store=list()
    
    store.append(dcc.Store(id=module+'name',data=module.rstrip('_')))
    
    newstore = params.default_store.copy()
    newstore.update(storeinit)
    
    for storeitem in newstore.keys():       
        store.append(dcc.Store(id=module+'store_'+storeitem, storage_type='session',data=newstore[storeitem]))
    
    return store

     
# if __name__ == '__main__':
    
