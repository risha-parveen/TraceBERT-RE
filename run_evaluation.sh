#!/bin/sh

# /app/output/'single_random_03-14 21-42-53_single_model'/final_model
# /app/output/'siamese2_random_03-17 16-18-33_siamese_model'/final_model
# /app/output/'single_online_06-01 07-35-13_online_single_model'/final_model

# github data evaluation

# cd /app/trace/trace_siamese

# python eval_trace_siamese.py \
#     --data_dir /app/trace/data/git_data/tonitaip-2020/postgresql-for-novices1 \
#     --model_path /app/output/'siamese2_random_03-17 16-18-33_siamese_model'/final_model \
#     --per_gpu_eval_batch_size 1 \
#     --exp_name 'postgres test eval'

cd /app/trace/trace_single

python eval_trace_single.py \
    --data_dir /app/trace/data/git_data/tonitaip-2020/postgresql-for-novices1 \
    --model_path /app/output/'single_online_06-01 07-35-13_online_single_model'/final_model \
    --per_gpu_eval_batch_size 1 \
    --exp_name 'postgres online eval'