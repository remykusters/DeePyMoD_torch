from deepymod_torch.constructors import build_network, build_coeff_vector
from deepymod_torch.training import train_cycle, train_mse

import torch.nn as nn
import torch

class deepmod_type(nn.Module):
    def __init__(self, config, network_constructor=build_network):
        super().__init__()
        self.config = config

        self.network = network_constructor(**self.config)
        self.coeff_vector_list = build_coeff_vector(self.network, self.config['library_args']['diff_order'])
        self.sparsity_mask_list = [torch.arange(coeff_vec.shape[0]) for coeff_vec in self.coeff_vector_list]
        
    def forward(self, input):
        prediction, time_deriv, theta = self.network(input)
        return prediction, time_deriv, theta
    
class DeepMod():
    def __init__(self, config):
        self.network = deepmod_type(config)

    def train(self, data, target, optimizer, max_iterations, l1=10**-5, type='single_cycle'):
        if type == 'single_cycle':
            train_cycle(data, target, self.network, optimizer, max_iterations, l1)
            
        elif type == 'mse':
            train_mse(self.network)

        elif type == 'full':
            train_cycle(data, target, self.network, optimizer, max_iterations, l1)
            #scaled_coeff_vector_list = [scaling(coeff_vector, theta, time_deriv) for coeff_vector, time_deriv in zip(coeff_vector_list, time_deriv_list)]
            #self.coeff_vector_list, self.sparsity_mask_list = zip(*[threshold(scaled_coeff_vector, coeff_vector) for scaled_coeff_vector, coeff_vector in zip(scaled_coeff_vector_list, coeff_vector_list)])
            #train_cycle(data, target, self.network, optimizer, max_iterations, l1=0)

    def __call__(self, input):
        prediction = self.network(input)
        return prediction

    def __getattr__(self, name):
        return self.network.__dict__[name]    
    
    def parameters(self):
        return self.network.parameters()
    
    @property
    def coeff_vector_list(self):
        return self.network.coeff_vector_list
        
