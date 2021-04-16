# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 19:47:10 2021

@author: aymer
"""

# good practice

from time import sleep
def process_data(data):
    sleep(3)
    print(data)
    return data

def main():
    data = "Hi"
    processed_data = process_data(data)
    return processed_data

if __name__ == "__main__":
    main()
    
    
    
# outside
import file as bp
bp.process_data