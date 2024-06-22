#!/bin/sh

# /app/output/single_random_03-14 21-42-53_single_model/final_model
# /app/output/siamese2_random_03-17 16-18-33_siamese_model/final_model
# /app/output/'single_online_06-01 07-35-13_online_single_model'/final_model

# github data evaluation

cd /app/trace/trace_single

python eval_trace_single.py \
    --data_dir /app/trace/data/git_data/niladricts/BusinessTampereTrafficMonitoring \
    --model_path /app/output/'single_online_06-01 07-35-13_online_single_model'/final_model \
    --per_gpu_eval_batch_size 16 \
    --exp_name 'trafficmonitoring online eval'