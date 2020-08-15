import logging

import torch
from torch import nn, autograd
import numpy as np
from torch.nn import CrossEntropyLoss
from tqdm import tqdm

logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)


def load_embd_from_file(embd_file_path):
    embd_matrix = []
    word2idx = {}
    idx = 0

    with open(embd_file_path, 'r', encoding='utf8') as fin:
        for line in tqdm(fin, "load embdding"):
            line = line.split()
            word = line[0]
            vec = [float(x) for x in line[1:]]
            embd_matrix.append(torch.tensor(vec, dtype=torch.float64))
            word2idx[word] = idx
            idx += 1
            if idx >= 100:
                break

    embd_dim = len(embd_matrix[0])
    embd_matrix.append(torch.from_numpy(np.random.normal(scale=0.6, size=(embd_dim,))))
    embd_matrix = torch.stack(embd_matrix)
    word2idx['__UNK__'] = idx
    embd_num = len(embd_matrix)
    return {"embd_matrix": embd_matrix,
            "word2idx": word2idx,
            "embd_dim": embd_dim,
            "embd_num": embd_num}


def create_emb_layer(embd_info, non_trainable=True):
    embd_num = embd_info['embd_num']
    embd_dim = embd_info['embd_dim']
    embd_layer = nn.Embedding(embd_num, embd_dim)
    embd_layer.load_state_dict({'weight': embd_info['embd_matrix']})
    if non_trainable:
        embd_layer.weight.requires_grad = False
    logger.info("finished building embedding layer")
    embd_info['embd_layer'] = embd_layer
    return embd_info


class classifyHeader(nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        self.hidden_size = hidden_size
        self.dense = nn.Linear(hidden_size, hidden_size)
        self.sigmoid = nn.Sigmoid()
        self.output_layer = nn.Linear(hidden_size, 2)

    def forward(self, nl_hidden, pl_hidden):
        multi_hidden = torch.mul(nl_hidden, pl_hidden)
        diff_hidden = torch.abs(nl_hidden - nl_hidden)
        fuse_hidden = multi_hidden + diff_hidden
        fuse_hidden = self.dense(fuse_hidden)
        sigmoid_hidden = self.sigmoid(fuse_hidden)
        logits = self.output_layer(sigmoid_hidden)
        return logits


class LSTMEncoder(nn.Module):
    def __init__(self, hidden_dim, embd_info):
        super().__init__()
        embd_info = create_emb_layer(embd_info)
        self.embedding = embd_info["embd_layer"]
        self.word2idx = embd_info['word2idx']
        self.embd_dim = embd_info['embd_dim']
        self.lstm = nn.LSTM(self.embd_dim, hidden_dim, num_layers=1, batch_first=True)

    def token_to_ids(self, tokens):
        id_vec = []
        for tk in tokens:
            tk = tk if tk in self.word2idx else "__UNK__"
            id = self.word2idx[tk]
            id_vec.append(id)
        id_tensor = torch.tensor(id_vec)
        return id_tensor

    def forward(self, input_ids):
        embd = self.embedding(input_ids)
        output, (last_hidden, last_cell_state) = self.lstm(embd)
        return last_hidden


class RNNTracer(nn.Module):
    def __init__(self, hidden_dim, embd_info):
        super().__init__()
        # self.embd_info =  load_embd_from_file(embd_file_path)
        self.embd_info = embd_info
        self.nl_encoder = LSTMEncoder(hidden_dim, self.embd_info)
        self.pl_encoder = LSTMEncoder(hidden_dim, self.embd_info)
        self.cls = classifyHeader(hidden_dim)

    def forward(self, nl_input, pl_input, label=None):
        nl_hidden = self.nl_encoder(nl_input)
        pl_hidden = self.pl_encoder(pl_input)
        logits = self.cls(nl_hidden, pl_hidden)
        output_dict = {'logits': logits}
        if label is not None:
            loss_fct = CrossEntropyLoss()
            rel_loss = loss_fct(logits.view(-1, 2), label.view(-1))
            output_dict['loss'] = rel_loss
        return output_dict

    def get_sim_score(self, text_hidden, code_hidden):
        logits = self.cls(text_hidden, code_hidden)
        sim_scores = torch.softmax(logits[-1], 1).data.tolist()
        return [x[1] for x in sim_scores]

    def get_nl_hidden(self, nl_input):
        nl_hidden = self.nl_encoder(nl_input)
        return nl_hidden

    def get_pl_hidden(self, pl_input):
        pl_hidden = self.pl_encoder(pl_input)
        return pl_hidden


if __name__ == "__main__":
    embd_info = create_emb_layer("./we/glove.6B.300d.txt")
    sent1 = ["this", "is", "sent1", "false"]
    sent2 = ["ok", "cool"]
    sent3 = ['that', "the"]

    rt = RNNTracer(hidden_dim=100)
    input_1 = rt.pl_encoder.token_to_ids(sent1)
    input_2 = rt.pl_encoder.token_to_ids(sent2)
    input_3 = rt.nl_encoder.token_to_ids(sent3)

    nl = input_1.view(1, -1)
    pl = input_2.view(1, -1)

    nl_hidden = rt.get_nl_hidden(nl)
    pl_hidden = rt.get_pl_hidden(pl)
    logits = rt(nl, pl)
    print(logits)

    score = rt.get_sim_score(text_hidden=nl_hidden, code_hidden=pl_hidden)
    print(score)
    # idx = embd_info['word2idx']['frog']
    # logger.info(embd_info['embd_matrix'][0])
    # embd = embd_info['embd_layer'](torch.tensor([[1, 2, 3], [4, 5, 6]]))
    # logger.info(embd)