#Convenutional NNs
import os
import cv2
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

REBBUILD_DATA = False
device = torch.device("cuda:0")

def fwd_pass(X, y, train= False):
	optimizer = optim.Adam(net.parameters(), lr = 0.001)
	loss_function = nn.MSELoss()
	if train:
		net.zero_grad()
	outputs = net(X)
	matches = [torch.argmax(i) == torch.argmax(j) for i, j in zip(outputs,y)]
	acc = matches.count(True)/len(matches)
	loss = loss_function(outputs, y)

	if train:
		loss.backward()
		optimizer.step()
	return acc, loss
def test(size=32):
	random_start = np.random.randint(len(test_X)-size)
	X,y = test_X[random_start:random_start+size], test_y[random_start:random_start+size]
	with torch.no_grad():
		val_acc, val_loss =fwd_pass(X.view(-1,1,50,50).to(device), y.to(device))
	return val_acc, val_loss

def train():
	BATCH_SIZE = 100
	EPOCHS = 5
	for epoch in range(EPOCHS):
		for i in tqdm(range(0, len(train_X), BATCH_SIZE)):
			batch_X = train_X[i:i+BATCH_SIZE].view(-1,1,50,50).to(device)
			batch_y = train_y[i:i+BATCH_SIZE].to(device)

			acc, loss = fwd_pass (batch_X, batch_y, train=True)
			if i %50 ==0:
				val_acc, val_loss = test(size=100)
				print(f"Acc {val_acc}, Loss {val_loss}")

class DogvCat():
	IMG_SIZE = 50
	CATS="pets/PetImages/Cat"
	DOGS="pets/PetImages/Dog"
	LABELS ={CATS: 0, DOGS: 1}
	training_data=[]
	catcount = 0
	dogcount = 0

	def make_training(self): 
	#assignging cat/dog image to one hot coded list. 
	#If image exists in the dog file the dog placeholder will be hot 
	#same for cat
		for label in self.LABELS:
			print (label)
			for f in tqdm(os.listdir(label)):
				try:
					path = os.path.join(label,f)
					#change image to grayscale and 50x50
					img = cv2.imread(path,cv2.IMREAD_GRAYSCALE)
					img = cv2.resize(img, (self.IMG_SIZE, self.IMG_SIZE))
					#take image data put it into list and put one hot encoding of dog or cat in list
					#makes training data a lol
					self.training_data.append([np.array(img),np.eye(2)[self.LABELS[label]]])


					if label == self.CATS:
						self.catcount +=1
					elif label == self.DOGS:
						self.dogcount +=1

				except Exception as e:
					pass

		np.random.shuffle(self.training_data)
		np.save("training_data.npy", self.training_data)
		print ("Cats ", self.catcount)
		print ("Dogs ", self.dogcount)

class Net(nn.Module):
	def __init__(self):
		super().__init__()
		self.conv1 = nn.Conv2d(1,32,5)
		self.conv2 = nn.Conv2d(32,64,5)
		self.conv3 = nn.Conv2d(64,128,5)
		x = torch.randn(50,50).view(-1,1,50,50)
		self._to_linear = None
		self.convs(x)
		self.fc1 = nn.Linear(self._to_linear, 512)
		self.fc2 = nn.Linear(512, 2)
		

	def convs(self, x):
		x = F.max_pool2d(F.relu(self.conv1(x)), (2,2))
		x = F.max_pool2d(F.relu(self.conv2(x)), (2,2))
		x = F.max_pool2d(F.relu(self.conv3(x)), (2,2))
		if self._to_linear is None:
			self._to_linear = x[0].shape[0]*x[0].shape[1]*x[0].shape[2]
		return x 

	def forward(self, x):
		x = self.convs(x)
		x= x.view(-1, self._to_linear)
		x = F.relu(self.fc1(x))
		x = self.fc2(x)
		return F.softmax(x, dim=1)





if REBBUILD_DATA:
	dogsvcats = DogvCat()
	dogsvcats.make_training()



training_data = np.load("training_data.npy", allow_pickle=  True)
'''show training data of cat/dog as images
plt.imshow(training_data[0][0],cmap="gray")
plt.show()
'''
BATCH_SIZE = 100
EPOCHS = 20


X = torch.Tensor([i[0] for i in training_data]).view(-1,50,50)
X = X/255.0
y = torch.Tensor([i[1] for i in training_data])

VAL_PCT = 0.1
val_Size = int(len(X)*VAL_PCT)

train_X= X[:-val_Size].to(device)

train_y =y[:-val_Size].to(device)

test_X= X[-val_Size:].to(device)
test_y =y[-val_Size:].to(device)

net= Net().to(device)

train()



