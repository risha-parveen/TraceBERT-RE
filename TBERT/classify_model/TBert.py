import os

import torch
from torch import nn
from torch.nn import CrossEntropyLoss
from transformers import PreTrainedModel, BertConfig, AutoTokenizer, AutoModel
from transformers.modeling_bert import BertPooler


# class AveragePooler(nn.Module):
#     def __init__(self, config):
#         super().__init__()
#         self.dense = nn.Linear(config.hidden_size, config.hidden_size)
#         self.activation = nn.Tanh()
#
#     def forward(self, hidden_states):
#         # We "pool" the model by averaging he hidden state corresponding to all tokens
#         first_token_tensor = hidden_states[:, 0]
#         pooled_output = self.dense(first_token_tensor)
#         pooled_output = self.activation(pooled_output)
#         return pooled_output

# class RelationClassifyHeader(nn.Module):
#     def __init__(self, config):
#         super().__init__()
#         config.is_decoder = True
#         self.relation_layer = BertLayer(config)
#         config.is_decoder = False
#         self.regression_header = BertOnlyNSPHead(config)
#         self.pooler = BertPooler(config)
#
#     def forward(self, code_hidden, text_hidden, code_attention_mask, text_attention_mask):
#         sequence_output = self.relation_layer(text_hidden, text_attention_mask, 1, code_hidden, code_attention_mask,)
#         pooled_output = self.pooler(sequence_output[0])
#         seq_relationship_score = self.regression_header(pooled_output)
#         return seq_relationship_score


class AvgPooler(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.hidden_size = config.hidden_size
        self.pooler = torch.nn.AdaptiveAvgPool2d((1, config.hidden_size))
        # self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        # self.activation = nn.Tanh()
        # self.activation = nn.ReLU()

    def forward(self, hidden_states):
        # pool_hidden = self.pooler(hidden_states).view(-1, self.hidden_size)
        # return self.activation(self.dense(pool_hidden))
        return self.pooler(hidden_states).view(-1, self.hidden_size)


class RelationClassifyHeader2(nn.Module):
    """
    H2:
    use averaging pooling across tokens to replace first_token_pooling
    """

    def __init__(self, config):
        super().__init__()
        self.hidden_size = config.hidden_size
        self.code_pooler = AvgPooler(config)
        self.text_pooler = AvgPooler(config)
        self.output_layer = nn.Linear(config.hidden_size * 3, 2)
        # self.dense_layer = nn.Linear(config.hidden_size * 3, config.hidden_size)
        # self.relation_layer = nn.Linear(config.hidden_size, 2)

    def forward(self, code_hidden, text_hidden):
        pool_code_hidden = self.code_pooler(code_hidden)
        pool_text_hidden = self.text_pooler(text_hidden)
        diff_hidden = torch.abs(pool_code_hidden - pool_text_hidden)
        concated_hidden = torch.cat((pool_code_hidden, pool_text_hidden), 1)
        concated_hidden = torch.cat((concated_hidden, diff_hidden), 1)
        # _hidden = F.relu(self.dense_layer(concated_hidden))
        # seq_relationship_score = self.relation_layer(_hidden)
        # return seq_relationship_score
        return self.output_layer(concated_hidden)


class RelationClassifyHeader_no_transformer(nn.Module):
    """
    H1:
    Problem with this head is that the loss converge at a very high value
    """

    def __init__(self, config):
        super().__init__()
        self.relation_layer = nn.Linear(config.hidden_size * 2, 2)
        self.nl_pooler = BertPooler(config)
        self.pl_pooler = BertPooler(config)

    def forward(self, code_hidden, text_hidden, code_attention_mask, text_attention_mask):
        pool_code_hidden = self.pl_pooler(code_hidden)
        pool_text_hidden = self.nl_pooler(text_hidden)
        concated_hidden = torch.cat((pool_code_hidden, pool_text_hidden), 1)
        seq_relationship_score = self.relation_layer(concated_hidden)
        return seq_relationship_score


class TBert(PreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        cbert_model = "huggingface/CodeBERTa-small-v1"
        # nbert_model = "bert-base-uncased"
        # nbert_model = "roberta-base"
        nbert_model = "huggingface/CodeBERTa-small-v1"

        self.ctokneizer = AutoTokenizer.from_pretrained(cbert_model)
        self.cbert = AutoModel.from_pretrained(cbert_model)

        self.ntokenizer = AutoTokenizer.from_pretrained(nbert_model)
        self.nbert = AutoModel.from_pretrained(nbert_model)
        # self.cls = RelationClassifyHeader_no_transformer(config)
        self.cls = RelationClassifyHeader2(config)

    def forward(
            self,
            code_ids=None,
            code_attention_mask=None,
            text_ids=None,
            text_attention_mask=None,
            relation_label=None):
        c_hidden = self.nbert(code_ids, attention_mask=code_attention_mask)[0]
        n_hidden = self.cbert(text_ids, attention_mask=text_attention_mask)[0]

        logits = self.cls(c_hidden, n_hidden)
        output_dict = {"logits": logits}
        if relation_label is not None:
            loss_fct = CrossEntropyLoss()
            # loss_fct = BCEWithLogitsLoss()
            rel_loss = loss_fct(logits.view(-1, 2), relation_label.view(-1))
            output_dict['loss'] = rel_loss
        return output_dict  # (rel_loss), rel_score

    def create_nl_embed(self, input_ids, attention_mask):
        return self.nbert(input_ids, attention_mask)

    def create_pl_embed(self, input_ids, attention_mask):
        return self.cbert(input_ids, attention_mask)


# debug
if __name__ == "__main__":
    config = BertConfig()
    t_bert = TBert(config)
    t_bert.state_dict()['my_flag'] = '1024'
    torch.save(t_bert.state_dict(), "./output/t_bert_state.pt")
    recovered_model = TBert(config)
    recovered_model.load_state_dict(torch.load("./output/t_bert_state.pt"))
    print(recovered_model.state_dict()['my_flag'])

    # s1 = 'def prepare_inputs_for_generation(self, input_ids, **kwargs): return {"input_ids": input_ids}'
    # s2 = 'prepare inputs for generation'
    # config.is_decoder = True
    # c_input_ids = t_bert.create_embd(s1, t_bert.ctokneizer)
    # n_input_ids = t_bert.create_embd(s2, t_bert.ntokenizer)
    # recovered_model.eval()
    # res = recovered_model(code_ids=c_input_ids,
    #                       text_ids=n_input_ids,
    #                       )
    # print(res)