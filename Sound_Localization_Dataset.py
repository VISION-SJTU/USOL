import os,glob,json
import torch
import numpy as np 
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import torch.nn.functional
from PIL import Image
from random import randint
from tqdm import tqdm
import time
import random
from random import choice
import math
import pdb
import scipy
import scipy.io as sio
import cv2
import pickle

def localization_gt_loader(sample, annotation_path=''):
	video_path = sample.replace('\n','')
	words = [word.replace('\n','') for word in video_path.split('/')]
	video_name = words[-1][:-4]
	path = annotation_path+'/'+video_name+'.mat'
	worker_gt = np.zeros((1,400))
	w_a = 1
	w_m = 1
	if annotation_path!='' and os.path.exists((path)):
		gt_file = sio.loadmat(path)
		# gt = (gt_file['gt_box20'])
		gt = (gt_file['gt20'])
		n_workers = gt.shape[2]
		worker = randint(0,n_workers-1)
		worker_gt_val = gt[:,:,worker]
		worker_gt = np.reshape(worker_gt_val,(1,400))
	else:
		w_a = 0
	weights = np.zeros((2))
	weights[0] = w_a
	weights[1] = w_m
	worker_gt_t = torch.from_numpy(worker_gt).view(1,400).float()
	weights_t = torch.from_numpy(weights)
	return worker_gt_t, weights_t


def audio_loader(sample, neg_sample):
	# Get positive audio
	video_path = sample.replace('\n','')
	words = [word.replace('\n','') for word in video_path.split('/')]
	video_name = words[-1][:-4]
	audio_file = video_name+'.mat'
	audio_path = video_path + '/' + audio_file
	pos_sound_file = sio.loadmat(audio_path)
	pos_sound = pos_sound_file['x']
	pos_sound = np.asarray(pos_sound) # CHECK THE SIZE!
	pos_sound_tensor = torch.from_numpy(pos_sound).squeeze().float()

	# Get negative audio
	neg_video_path = neg_sample.replace('\n','')
	neg_words = [neg_word.replace('\n','') for neg_word in neg_video_path.split('/')]
	neg_video_name = neg_words[-1][:-4]
	neg_audio_file = neg_video_name+'.mat'
	neg_audio_path = neg_video_path + '/' + neg_audio_file
	neg_sound_file = sio.loadmat(neg_audio_path)
	neg_sound = neg_sound_file['x']
	neg_sound = np.asarray(neg_sound) # CHECK THE SIZE!
	neg_sound_tensor = torch.from_numpy(neg_sound).squeeze().float()

	return pos_sound_tensor, neg_sound_tensor

def image_loader(sample):
	video_path = sample.replace('\n','')
	all_frames = glob.glob(video_path+'/*.jpg')
	# all_frames = sorted(all_frames)
	first_image_path = str(all_frames[0])
	first_image = Image.open(first_image_path).convert('RGB')
	return first_image

def detection_loader(sample):
	numShowRects = 50
	thres = 0.02
	bottom_up_attention_path = sample.replace('\n', '') + '/ss_boxes.pkl'
	bottom_up_filename = open(bottom_up_attention_path, 'rb')
	bot_map = np.zeros((320, 320))
	all_regions = pickle.load(bottom_up_filename)
	for i, rect in enumerate(all_regions):
		if (i < numShowRects):
			x, y, w, h = rect  # bounding box top, left, width, height
			# cv2.rectangle(imOut, (x, y), (x + w, y + h), (0, 255, 0), 1)
			bot_map[y:y+h, x:x+w] += np.ones((h, w)) * 0.02
		else:
			break
	bot_map = cv2.resize(bot_map, (20, 20))
	bot_map = np.reshape(bot_map, (400))
	pos = bot_map > thres
	return torch.from_numpy(pos).float()

class Sound_Localization_Dataset(Dataset):
	def __init__(self, dataset_file, mode, annotation_path):

		self.mode = mode
		self.annotation_path = annotation_path
		ds = open(dataset_file)
		lines = ds.readlines()

		self.data = lines

		self.preprocess_tr = transforms.Compose([transforms.Scale((320,320)),transforms.RandomGrayscale(p=0.5), transforms.RandomVerticalFlip(p=0.5),transforms.RandomHorizontalFlip(p=0.5), transforms.ColorJitter(brightness=0.5,contrast=0.5,saturation=0.5,hue=0.5), transforms.ToTensor(),transforms.Normalize(mean=[0.485, 0.456, 0.406],std=[0.229, 0.224, 0.225])])
		self.preprocess_te = transforms.Compose([transforms.Scale((320,320)),transforms.ToTensor(),transforms.Normalize(mean=[0.485, 0.456, 0.406],std=[0.229, 0.224, 0.225])])
	def __getitem__(self,index):
		datum = self.data[index]
		# Get negative index and negative sample
		neg_index = choice([r for r in range(0,len(self.data)) if r not in [index]])
		neg_datum = self.data[neg_index]
		# Get video frames
		first_frame = image_loader(datum)
		if self.mode=='train':
			bottom_up_map = detection_loader(datum)
		else:
			bottom_up_map = torch.zeros((400),dtype=torch.float)
		if self.mode!='test':
			first_frame_t = self.preprocess_tr(first_frame).float()
		else:
			first_frame_t = self.preprocess_te(first_frame).float()
		pos_audio_t,neg_audio_t = audio_loader(datum, neg_datum)
		worker_gt_t, weigths_t = localization_gt_loader(datum,self.annotation_path)
		
		return first_frame_t, pos_audio_t, neg_audio_t, bottom_up_map, worker_gt_t, weigths_t, datum

	def __len__(self):
		return len(self.data)



