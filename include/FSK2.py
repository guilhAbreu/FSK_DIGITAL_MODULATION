#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 22:33:41 2019

@author: guilherme
"""

#importing libraries
import matplotlib.pyplot as plt
import numpy as np
from include.app_decoder import app_decoder

import os, sys

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

def FSK2_demodulation(data, Fs, plot = False, n_samples = 0, baudRate = 20):
    
    F1=800
    F2=1200
    t_wave=np.arange(0,1/baudRate,1/Fs)
    wave1=np.cos(2*np.pi*F1*t_wave)
    wave2=np.cos(2*np.pi*F2*t_wave)
    
    end_bit = int((n_samples/baudRate)*Fs)
    
    if end_bit == 0:
        end_bit = len(data)
    
    # get data
    data  = data[:end_bit]
    t     = np.arange(0,len(data)/Fs,1/Fs)
    
    if plot:
        plt.figure(figsize=(32,32))
        plt.plot(t,data)
        plt.title('Sinal recebido')
        plt.show()
    
    # aplly matched filter
    matched1 = np.convolve(data,np.flip(wave1))
    matched2 = np.convolve(data,np.flip(wave2))
    
    # filter sampling of each bit
    step=int(Fs/baudRate)
    
    if plot:
        y1_samples = matched1[step::step]
        y2_samples = matched2[step::step]
        t_samples  = np.arange(step/Fs,t[-1]+step/Fs,step/Fs)
        
        plt.figure(figsize=(16,16))
        plt.plot(t,matched1[:len(t)],'b')
        plt.title('Saida e Amostragem do Filtro Casado1')
        plt.plot(t_samples,y1_samples,'or')
        plt.show()
        
        plt.figure(figsize=(16,16))
        plt.plot(t,matched2[:len(t)],'b')
        plt.title('Saida e Amostragem do Filtro Casado2')
        plt.plot(t_samples,y2_samples,'or')
        plt.show()
    
    y1 = np.convolve(np.abs(matched1),np.ones((int(len(t_wave)/2))))
    y2 = np.convolve(np.abs(matched2),np.ones((int(len(t_wave)/2))))
    
    y1_samples = y1[step::step]
    y2_samples = y2[step::step]
    t_samples  = np.arange(step/Fs,t[-1]+step/Fs,step/Fs)
    
    if plot:
        plt.figure(figsize=(16,16))
        plt.plot(t,y1[:len(t)],'b')
        plt.plot(t_samples,y1_samples,'or')
        plt.title('Deteccao e Amostragem da Envoltoria 1')
        plt.show()
        
        plt.figure(figsize=(16,16))
        plt.plot(t,y2[:len(t)],'b')
        plt.plot(t_samples,y2_samples,'or') 
        plt.title('Deteccao e Amostragem da Envoltoria 2')
        plt.show()
    
    # load header
    header_file = open("header.txt", 'r')
    h = header_file.readline()
    header_file.close()
    h = h.replace('[','').replace(']','')
    header = np.asarray([int(x) for x in h.split(',')])
    
    # make a decision
    output = y2_samples - y1_samples
    output[output > 0] = 1
    output[output < 0] = 0
    
    # get the optimized delta
    corr = np.correlate(output, header)
    
    with HiddenPrints():
        ta = 0
        while len(corr) > len(header) and ta < 0.7:
            delta = np.argmax(corr)
            msg_bits = (output.astype("uint8"))[delta+len(header):]
            ta = app_decoder(msg_bits)
            corr = np.delete(corr, delta)
    app_decoder(msg_bits)
    
    
    return msg_bits