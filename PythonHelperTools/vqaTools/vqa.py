__author__ = 'aagrawal'
__version__ = '0.9'

# Interface for accessing the VQA dataset.

# This code is based on the code written by Tsung-Yi Lin for MSCOCO Python API available at the following link: 
# (https://github.com/pdollar/coco/blob/master/PythonAPI/pycocotools/coco.py).

# The following functions are defined:
#  VQA        - VQA class that loads VQA annotation file and prepares data structures.
#  getQuesIds - Get question ids that satisfy given filter conditions.
#  getImgIds  - Get image ids that satisfy given filter conditions.
#  loadQA     - Load questions and answers with the specified question ids.
#  showQA     - Display the specified questions and answers.
#  loadRes    - Load result file and create result object.

# Help on each function can be accessed by: "help(COCO.function)"

import json
import datetime
import copy
import shutil
import os

class VQA:
	def __init__(self, annotation_file=None, question_file=None):
		"""
       	Constructor of VQA helper class for reading and visualizing questions and answers.
        :param annotation_file (str): location of VQA annotation file
        :return:
		"""
        # load dataset
		self.dataset = {}
		self.questions = {}
		self.qa = {}
		self.qqa = {}
		self.imgToQA = {}
		if not annotation_file == None and not question_file == None:
			print('loading VQA annotations and questions into memory...')
			time_t = datetime.datetime.utcnow()
			dataset = json.load(open(annotation_file, 'r'))
			questions = json.load(open(question_file, 'r'))
			print(datetime.datetime.utcnow() - time_t)
			self.dataset = dataset
			self.questions = questions
			self.createIndex()

	def dumpData(self, qIds, annotation_file, question_file, source_captions, caption_file, img_dir, new_img_dir, data_subtype):
		"""
		Extracts questions defined by qIds and stores the respective annotations, questions, and captions.

		:param qIds (list): list of question ids
		:param annotation_file (string): where to store annotations
		:param question_file (string): where to store question objects
		:source_captions (string): where coco captions are stored
		:caption_file (string): where to store caption objects for questions in qIds
		:img_dir (string): directory of coco images
		:new_img_dir (string): directory of extracted images
		:data_subtype (string): data subtype
		"""
		# extract annotations and question objects
		anns = [ann for ann in self.dataset['annotations'] if ann['question_id'] in qIds]
		qs = [q for q in self.questions['questions'] if q['question_id'] in qIds]
		dataset_copy = copy.deepcopy(self.dataset)
		questions_copy = copy.deepcopy(self.questions)
		dataset_copy['annotations'] = anns
		questions_copy['questions'] = qs
		json.dump(dataset_copy, open(annotation_file, 'w'))
		json.dump(questions_copy, open(question_file, 'w'))

		# extract image captions
		imgs = [q['image_id'] for q in self.questions['questions'] if q['question_id'] in qIds]
		source = json.load(open(source_captions, 'r'))
		# captions = [c for c in source['annotations'] if c['image_id'] in imgs]
		captions = {}
		for c in source['annotations']:
			id = c['image_id']
			if id in imgs:
				if id not in captions:
					captions[id] = "Futuristic. "
				captions[id] += c['caption'] + " "
		json.dump(captions, open(caption_file, 'w'))
		print(len(captions))

		# create new image folder
		if os.path.exists(new_img_dir):
			shutil.rmtree(new_img_dir)
		os.mkdir(new_img_dir)
		for id in imgs:
			imgFilename = 'COCO_' + data_subtype + '_'+ str(id).zfill(12) + '.jpg'
			if os.path.isfile(img_dir + imgFilename):
				shutil.copy(img_dir + imgFilename, new_img_dir + imgFilename)
			else:
				print("Error: " + str(id) + " not found")

	def createIndex(self):
        # create index
		print('creating index...')
		# dictionary comprehension of ids to empty arrays
		imgToQA = {ann['image_id']: [] for ann in self.dataset['annotations']}
		qa =  {ann['question_id']:       [] for ann in self.dataset['annotations']}
		qqa = {ann['question_id']:       [] for ann in self.dataset['annotations']}
		for ann in self.dataset['annotations']:
			imgToQA[ann['image_id']] += [ann] # add annotations to each image
			qa[ann['question_id']] = ann # add annotations for each question id
		for ques in self.questions['questions']: 
			qqa[ques['question_id']] = ques # add questions to question id
		print('index created!')

		# create class members
		self.qa = qa
		self.qqa = qqa
		self.imgToQA = imgToQA

	def info(self):
		"""
		Print information about the VQA annotation file.
		:return:
		"""
		for key, value in self.datset['info'].items():
			print('%s: %s'%(key, value))

	def getQuesIds(self, imgIds=[], quesTypes=[], ansTypes=[]):
		"""
		Get question ids that satisfy given filter conditions. default skips that filter
		:param 	imgIds    (int array)   : get question ids for given imgs
				quesTypes (str array)   : get question ids for given question types
				ansTypes  (str array)   : get question ids for given answer types
		:return:    ids   (int array)   : integer array of question ids
		"""
		imgIds 	  = imgIds    if type(imgIds)    == list else [imgIds]
		quesTypes = quesTypes if type(quesTypes) == list else [quesTypes]
		ansTypes  = ansTypes  if type(ansTypes)  == list else [ansTypes]

		if len(imgIds) == len(quesTypes) == len(ansTypes) == 0:
			anns = self.dataset['annotations']
		else:
			if not len(imgIds) == 0:
				anns = sum([self.imgToQA[imgId] for imgId in imgIds if imgId in self.imgToQA],[])
			else:
 				anns = self.dataset['annotations']
			anns = anns if len(quesTypes) == 0 else [ann for ann in anns if ann['question_type'] in quesTypes]
			anns = anns if len(ansTypes)  == 0 else [ann for ann in anns if ann['answer_type'] in ansTypes]
		ids = [ann['question_id'] for ann in anns]
		return ids

	def getImgIds(self, quesIds=[], quesTypes=[], ansTypes=[]):
		"""
		Get image ids that satisfy given filter conditions. default skips that filter
		:param quesIds   (int array)   : get image ids for given question ids
               quesTypes (str array)   : get image ids for given question types
               ansTypes  (str array)   : get image ids for given answer types
		:return: ids     (int array)   : integer array of image ids
		"""
		quesIds   = quesIds   if type(quesIds)   == list else [quesIds]
		quesTypes = quesTypes if type(quesTypes) == list else [quesTypes]
		ansTypes  = ansTypes  if type(ansTypes)  == list else [ansTypes]

		if len(quesIds) == len(quesTypes) == len(ansTypes) == 0:
			anns = self.dataset['annotations']
		else:
			if not len(quesIds) == 0:
				anns = sum([self.qa[quesId] for quesId in quesIds if quesId in self.qa],[])
			else:
				anns = self.dataset['annotations']
			anns = anns if len(quesTypes) == 0 else [ann for ann in anns if ann['question_type'] in quesTypes]
			anns = anns if len(ansTypes)  == 0 else [ann for ann in anns if ann['answer_type'] in ansTypes]
		ids = [ann['image_id'] for ann in anns]
		return ids

	def loadQA(self, ids=[]):
		"""
		Load questions and answers with the specified question ids.
		:param ids (int array)       : integer ids specifying question ids
		:return: qa (object array)   : loaded qa objects
		"""
		if type(ids) == list:
			return [self.qa[id] for id in ids]
		elif type(ids) == int:
			return [self.qa[ids]]

	def showQA(self, anns):
		"""
		Display the specified annotations.
		:param anns (array of object): annotations to display
		:return: None
		"""
		if len(anns) == 0:
			return 0
		for ann in anns:
			quesId = ann['question_id']
			print("Question: %s" %(self.qqa[quesId]['question']))
			for ans in ann['answers']:
				print("Answer %d: %s" %(ans['answer_id'], ans['answer']))
		
	def loadRes(self, resFile, quesFile):
		"""
		Load result file and return a result object.
		:param   resFile (str)     : file name of result file
		:return: res (obj)         : result api object
		"""
		res = VQA()
		res.questions = json.load(open(quesFile))
		res.dataset['info'] = copy.deepcopy(self.questions['info'])
		res.dataset['task_type'] = copy.deepcopy(self.questions['task_type'])
		res.dataset['data_type'] = copy.deepcopy(self.questions['data_type'])
		res.dataset['data_subtype'] = copy.deepcopy(self.questions['data_subtype'])
		res.dataset['license'] = copy.deepcopy(self.questions['license'])

		print('Loading and preparing results...     ')
		time_t = datetime.datetime.utcnow()
		anns    = json.load(open(resFile))
		assert type(anns) == list, 'results is not an array of objects'
		annsQuesIds = [ann['question_id'] for ann in anns]
		assert set(annsQuesIds) == set(self.getQuesIds()), \
		'Results do not correspond to current VQA set. Either the results do not have predictions for all question ids in annotation file or there is atleast one question id that does not belong to the question ids in the annotation file.'
		for ann in anns:
			quesId 			     = ann['question_id']
			if res.dataset['task_type'] == 'Multiple Choice':
				assert ann['answer'] in self.qqa[quesId]['multiple_choices'], 'predicted answer is not one of the multiple choices'
			qaAnn                = self.qa[quesId]
			ann['image_id']      = qaAnn['image_id'] 
			ann['question_type'] = qaAnn['question_type']
			ann['answer_type']   = qaAnn['answer_type']
		print('DONE (t=%0.2fs)'%((datetime.datetime.utcnow() - time_t).total_seconds()))

		res.dataset['annotations'] = anns
		res.createIndex()
		return res
