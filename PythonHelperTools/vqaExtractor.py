from vqaTools.vqa import VQA
import random
import skimage.io as io
import matplotlib.pyplot as plt
import os

dataDir		='../../VQA'
versionType ='v2_' # this should be '' when using VQA v2.0 dataset
newVersionType='v3_'
taskType    ='OpenEnded' # 'OpenEnded' only for v2.0. 'OpenEnded' or 'MultipleChoice' for v1.0
dataType    ='mscoco'  # 'mscoco' only for v1.0. 'mscoco' for real and 'abstract_v002' for abstract for v1.0.
dataSubType ='val2014'
annFile     ='%s/Annotations/%s%s_%s_annotations.json'%(dataDir, versionType, dataType, dataSubType)
quesFile    ='%s/Questions/%s%s_%s_%s_questions.json'%(dataDir, versionType, taskType, dataType, dataSubType)
newAnnFile  ='%s/Annotations/%s%s_%s_annotations.json'%(dataDir, newVersionType, dataType, dataSubType) # store extracted annotations
newQuesFile ='%s/Questions/%s%s_%s_%s_questions.json'%(dataDir, newVersionType, taskType, dataType, dataSubType) # store extracted questions
sourceCaptions ='%s/Images/%s/captions_%s.json' %(dataDir, dataType, dataSubType) # location of captions file
newCaptions = '%s/Images/%s/captions_%s%s.json' %(dataDir, dataType, newVersionType, dataSubType) # store extracted captions
imgDir 		= '%s/Images/%s/%s/' %(dataDir, dataType, dataSubType)
newImgDir   = '%s/Images/%s/%s%s/' %(dataDir, dataType, newVersionType, dataSubType)

# extracts k samples for each answer type
vqa=VQA(annFile, quesFile)
ansTypes = ('yes/no', 'number', 'other')
qs = []
for ansType in ansTypes:
    qIds = vqa.getQuesIds(ansTypes=ansType);   
    randomQ = random.choices(qIds, k = 50) # number of questions of each type to extract
    qs += randomQ
vqa.dumpData(qs, newAnnFile, newQuesFile, sourceCaptions, newCaptions, imgDir, newImgDir, dataSubType)