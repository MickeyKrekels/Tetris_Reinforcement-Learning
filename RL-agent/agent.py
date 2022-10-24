from collections import deque
from model import Linear_QNet , QTrainer

import numpy as np
import random
import torch
import sys

sys.path.append("..")
from game.tetris import Piece, shapes


MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:
    def __init__(self,model_path = ''):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9 
        self.memory = deque(maxlen=MAX_MEMORY) 
        self.model = Linear_QNet(11, 256, 3)
        if model_path != '':
            self.model = self.load_model(model_path)
            
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
    
    def get_state(self,game,offset_check = 10):
        point_l = Point(pos.x - offset_check, pos.y)
        point_r = Point(pos.x + offset_check, pos.y)
        point_u = Point(pos.x, pos.y - offset_check)
        point_d = Point(pos.x, pos.y + offset_check)
        
        dir_l = game.direction == Direction.EAST 
        dir_r = game.direction == Direction.WEST 
        dir_u = game.direction == Direction.NORTH
        dir_d = game.direction == Direction.SOUTH
        
        # this array are all the possible states and the agent will choose the best action 
        state = [ 

            # #---gives the agent an indication of where the boundary is by sampling the environment around the head location---#
            # (dir_r and game.check_collision(point_r)) or # Danger straight
            # (dir_l and game.check_collision(point_l)) or 
            # (dir_u and game.check_collision(point_u)) or 
            # (dir_d and game.check_collision(point_d)),
            # (dir_u and game.check_collision(point_r)) or # Danger right
            # (dir_d and game.check_collision(point_l)) or 
            # (dir_l and game.check_collision(point_u)) or 
            # (dir_r and game.check_collision(point_d)),
            # (dir_d and game.check_collision(point_r)) or # Danger left
            # (dir_u and game.check_collision(point_l)) or 
            # (dir_r and game.check_collision(point_u)) or 
            # (dir_l and game.check_collision(point_d)),
            
            # # Move direction
            # dir_l,dir_r,dir_u,dir_d,       
            


            ]
        
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

    def save_model(self):
        self.model.save()

    def load_model(self,path):
        return self.model.load(path)







        

