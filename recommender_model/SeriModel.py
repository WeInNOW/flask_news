import torch
import torch.nn as nn

class SeriModel(nn.Module):
    def save(self, path):
        torch.save(self.state_dict(), path)
    def load(self, path):
        self.load_state_dict(torch.load(path))