#!/usr/bin/env python
# coding: utf-8

"""
关键词相关度语义分析
Date: 2022-6-22
"""


import spacy
import pandas as pd
import numpy as np




#被比对的关键词
kw1 = [
'ice cude maker',
'pellet ice makers countertop',
'igloo ice makers countertop',
'machine',
'commercial ice machine',
'tabletop ice maker',
'opal ice machine nugget ice maker',
'ice maker small',
'opal nugget ice maker',
'profile ice maker',
'ge nugget ice maker',
'ge profile ice maker',
'craft ice maker',
'ice maker nugget ice for home',
'galanz',
'spaetzle maker',
'ge opal nugget ice maker',
'ice machines',
'sonic ice machine',
'newair ice maker',
'soft ice maker',
'ice machine maker',
'home ice maker',
'ice maker cleaner',
'euhomy ice maker',
'portable ice makers countertop prime clearance',
'portable ice machine',
'manitowoc ice machine',
'ge opal ice maker side tank',
'ice makers countertop self cleaning',
'frigidaire ice maker countertop',
'freeze drying equipment',
'ge opal',
'bullet ice cubes',
'outdoor ice maker',
'ice machine nugget ice maker',
'maquina de hielo',
'pebble ice machine',
'mini ice machine',
'top sellers',
'countertop ice machine',
'ice machine countertop',
'dream machine',
'small ice makers countertop',
'rv ice maker',
'silonn ice makers countertop',
'churros maker machine',
'commercial ice maker machine',
'magic chef ice maker',
'ice maker machine/ice makers',
'counter top ice makers made in usa',
'ice makers countertop pellet ice',
'ge opal ice maker',
'compact ice maker',
'i e maker counter top',
'ice maker that makes sonic ice',
'newair',
'ice maker frigidaire',
'ice maker commercial',
'crownful ice maker',
'counter ice machine',
'ive maker',
'ice maker under counter',
'undercounter ice maker machine',
'cosas para la cocina',
'ice maker machine for countertop',
'ice cube maker countertop',
'ikich ice maker',
'chewy ice maker',
'ice barrel',
'opal ice maker cleaning kit',
'nevera para carro',
'pellet ice machine',
'aglucky countertop ice maker',
'electric ice maker',
'small kitchen ice maker',
'opal 2.0 nugget ice maker',
'countertop icemaker',
'crush ice maker',
'hoshizaki ice machine',
'table top ice maker',
'ice and water dispenser',
'bullet ice maker',
'ice barrel cold therapy bath',
'12 volt ice maker',
'insignia ice maker',
'ice makers countertop crushed',
'mini ice cube maker',
'maquina de hielo para casa',
'sonic ice maker for home',
'countertop ice maker crushed ice',
'countertops',
'ice maker machine like sonic ice',
'cube ice maker',
'dry ice maker',
'new air ice machines countertop',
'ice maket',
'ice dispenser',
'crownful ice machine',
'small ice machine',
'lg ice maker',
'nugget ice maker sonic ice',
'flake ice machine',
'newair nugget ice maker',
'self cleaning ice makers countertop',
'sonic ice',
'crushed ice makers countertop sonic ice',
'portable ice makers',
'ice pellet maker machine',
'ice maker portable',
'hospital ice machine for home',
'countertop crushed ice maker',
'ice machine slushie maker',
'gevi nugget ice maker',
'ge profile',
'ge profile opal nugget ice maker',
'dreamiracle ice maker',
'countertop ice maker pellet ice',
'commercial nugget ice maker',
'ge profile opal side tank',
'ice maker sonic ice',
'small ice cube maker',
'maker',
'ge profile opal',
'ge opal ice maker cleaning kit',
'i e maker',
'frigidaire compact ice maker',
'edgestar ice maker',
'frigidaire nugget ice maker',
'ice maker nugget ice',
'opal ice machine',
'counter top ice machine',
'home ice makers countertop',
'ice making machine',
'ice cone maker',
'opal ice',
'kitchenaid ice maker',
'cheap ice maker',
'ice machines countertop',
'ice maker mini',
'small cube ice maker',
'counter ice maker machine',
'commercial ice machines',
'pellet ice',
'trituradora de hielo',
'ge profile ice maker countertop',
'vremi ice maker',
'ice maker ge',
'ice maker water dispenser',
'euhomy',
'mini ice maker machine',
'ice maker with water line',
'self cleaning ice maker',
'personal ice maker',
'countertop ice makers',
'automatic ice maker',
'opal cleaning kit for ice maker',
'portable ice machines countertop'
]



#出单的关键词
kw2 = ['ice maker', 'ice makers countertop', 'small ice maker', 'portable ice maker countertop']



def kw_similarity(kw1_tar, kw2_ref): #en_core_web_sm
    nlp = spacy.load('en_core_web_sm')
    Score = []
    for word1 in kw1_tar:
        for word2 in kw2_ref:
            score = nlp(word1).similarity(nlp(word2))
            Score.append(score)
    data = Score
    index = pd.MultiIndex.from_product([kw1_tar, kw2_ref])
    df = pd.DataFrame(data,index=index,columns=['Score'])
    df = df.reset_index().rename(columns={'level_0': '新关键词', 'level_1': '最相似已知词'})
    df['Max'] = df.groupby(by='新关键词')['Score'].transform('max')
    df = df[df['Score']==df['Max']].copy()
    df = df.reset_index(drop=True).drop(columns='Max')
    return df

if __name__ == '__main__':

    "get result "
    res = kw_similarity(kw1, kw2)
    # res.to
    res.to_csv('关键词相关度.csv')

