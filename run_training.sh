#!/bin/sh

# pretraining command

# python single_train.py \
#   --data_dir ../data/code_search_net/javascript \
#   --output_dir /app/output \
#   --per_gpu_train_batch_size 8 \
#   --per_gpu_eval_batch_size 8 \
#   --logging_steps 10 \
#   --save_steps 10000 \
#   --gradient_accumulation_steps 16 \
#   --num_train_epochs 8 \
#   --learning_rate 4e-5 \
#   --valid_num 200 \
#   --valid_step 10000 \
#   --neg_sampling random

# fine tuning command

cd /app/trace/trace_single

python train_trace_single.py \
    --data_dir /app/trace/data/git_data/keras-team/keras \
    --model_path /app/output/model/online_single_model \
    --output_dir /app/output \
    --per_gpu_train_batch_size 16 \
    --per_gpu_eval_batch_size 16 \
    --logging_steps 10 \
    --save_steps 10000 \
    --gradient_accumulation_steps 16 \
    --num_train_epochs 400 \
    --learning_rate 4e-5 \
    --valid_num 200 \
    --valid_step 10000 \
    --neg_sampling online