import logging
import os
from collections import defaultdict
from functools import partial
from multiprocessing.pool import Pool

import torch
from torch.utils.data import DataLoader
from tqdm.gui import tqdm

from model2 import CodeSearchNetReader, TBertProcessor
import pandas as pd

from model2.VSM_baseline.vsm_baseline import best_accuracy, topN_RPF


def convert_examples_to_dataset(examples, NL_tokenizer, PL_tokenizer, threads=1):
    """

    :param examples:
    :param NL_tokenizer:
    :param PL_tokenizer:
    :param is_training: if it is training/evaluation then do not add label as it not exist.
    :param threads:
    :return:
    """
    pos_features = []
    neg_features = []
    threads = min(threads, os.cpu_count())
    with Pool(threads) as p:
        annotate_ = partial(
            TBertProcessor().process_example,
            NL_tokenizer=NL_tokenizer,
            PL_tokenizer=PL_tokenizer,
            max_length=512
        )
        features = list(
            tqdm(
                p.imap(annotate_, examples, chunksize=32),
                desc="convert examples to positive features"
            )
        )

    rel_index = defaultdict(set)
    NL_index = dict()  # find instance by id
    PL_index = dict()
    nl_cnt = 0
    pl_cnt = 0
    for f in tqdm(features, desc="assign ids to examples"):
        # assign id to the features
        nl_id = "N{}".format(nl_cnt)
        pl_id = "P{}".format(pl_cnt)
        f[0]['id'] = nl_id
        f[1]['id'] = pl_id
        NL_index[nl_id] = f[0]
        PL_index[pl_id] = f[1]
        rel_index[nl_id].add(pl_id)
        nl_cnt += 1
        pl_cnt += 1

    for nl_cnt, nl_id in enumerate(NL_index):
        if nl_cnt > 100:
            break
        for pl_id in PL_index:
            if pl_id in rel_index[nl_id]:
                pos_features.append((NL_index[nl_id], PL_index[pl_id], 1))
            else:
                neg_features.append((NL_index[nl_id], PL_index[pl_id], 0))
    return pos_features, neg_features, NL_index, PL_index


if __name__ == "__main__":
    data_dir = "./data/code_search_net/python"
    model_path = ""
    device = 'cuda'
    cache_dir = os.path.join(data_dir, "cache")
    cached_file = os.path.join(cache_dir, "retrieval_eval.dat".format())
    eval_batch_size = 8

    logger = logging.getLogger(__name__)

    assert os.path.isfile(model_path)
    model = torch.load(os.path.join(model_path, 't_bert.pt'))
    model.to(device)

    nl_toknizer = model.ntokenizer
    pl_tokenizer = model.ctokneizer

    csr = CodeSearchNetReader(data_dir)
    examples = csr.get_examples('valid')
    pos, neg, NL_index, PL_index = convert_examples_to_dataset(examples, nl_toknizer, pl_tokenizer)
    instances = pos + neg
    dataset = TBertProcessor().features_to_data_set(instances, True)

    dataloader = DataLoader(dataset, batch_size=eval_batch_size)
    res = []
    for batch in tqdm(dataloader, desc="Evaluating"):
        model.eval()
        batch = tuple(t.to(device) for t in batch)
        with torch.no_grad():
            inputs = {
                "text_ids": batch[0],
                "text_attention_mask": batch[1],
                "code_ids": batch[2],
                "code_attention_mask": batch[3],
            }
            label = batch[4]
            nl_id = batch[5]
            pl_id = batch[6]
            outputs = model(**inputs)
            logit = outputs['logits']
            pred = logit.data[1]
            for n, p, pd, lb in zip(nl_id.tolist(), pl_id.tolist(), pred.tolist(), label.tolist()):
                res.append((n, p, pd, lb))
    df = pd.DataFrame()
    df['s_id'] = [x[0] for x in res]
    df['t_id'] = [x[1] for x in res]
    df['pred'] = [x[2] for x in res]
    df['label'] = [x[3] for x in res]
    print("evaluating...")
    best_accuracy(df, threshold_interval=1)
    topN_RPF(df, 3)