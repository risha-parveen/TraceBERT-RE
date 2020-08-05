python twin_train.py \
--data_dir ../data/code_search_net/python \
--output_dir ./output \
--fp16 \
--per_gpu_train_batch_size 8 \
--per_gpu_eval_batch_size 8 \
--logging_steps 10 \
--save_steps 2000 \
--gradient_accumulation_steps 8 \
--num_train_epochs 8 \
--learning_rate 4e-5 \
--valid_num 200 \
--valid_step 100 \
--neg_sampling random \
--overwrite
