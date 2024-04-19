FROM python:3.7

WORKDIR /app

COPY requirement.txt .

RUN pip install -U setuptools && \
    pip install -r requirement.txt \
    pip install torch==1.7.1+cu110 torchvision==0.8.2+cu110 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html

COPY . .

# github data training
WORKDIR /app/trace/trace_siamese

# CMD ["python", "train_trace_siamese.py", \
#     "--data_dir", "/app/trace/data/git_data/dbcli/pgcli", \
#     "--model_path", "/app/output/model/siamese_model", \
#     "--output_dir", "/app/output", \
#     "--per_gpu_train_batch_size", "16", \
#     "--per_gpu_eval_batch_size", "16", \
#     "--logging_steps", "10", \
#     "--save_steps", "10000", \
#     "--gradient_accumulation_steps", "16", \
#     "--num_train_epochs", "400", \
#     "--learning_rate", "4e-5", \
#     "--valid_num", "200", \
#     "--valid_step", "10000", \
#     "--neg_sampling", "random"]

# github data evaluation

CMD ["python", "eval_trace_siamese.py", "--data_dir", "/app/trace/data/git_data/EVCommunities/Components", \
    "--model_path", "/app/output/siamese2_random_03-17 16-18-33_siamese_model/final_model", \
    "--per_gpu_eval_batch_size", "32", "--exp_name", "EVCommunities eval"]

##################################################################################################################################################################################################################

# pretraining 
# WORKDIR /app/code_search/single

# CMD ["python", "single_train.py", \
#     "--data_dir", "../data/code_search_net/python", \
#     "--output_dir", "/app/output", \
#     "--per_gpu_train_batch_size", "8", \
#     "--per_gpu_eval_batch_size", "8", \
#     "--logging_steps", "10", \
#     "--save_steps", "10000", \
#     "--gradient_accumulation_steps", "16", \
#     "--num_train_epochs", "8", \
#     "--learning_rate", "4e-5", \
#     "--valid_num", "200", \
#     "--valid_step", "10000", \
#     "--neg_sampling", "random"]

#pretraining validation

# CMD ["python", "siamese2_eval.py", "--data_dir", "../data/code_search_net/python", "--model_path", "/app/output/siamese2_random_03-08 17-05-53_/final_model", "--per_gpu_eval_batch_size", "4", "--exp_name", "code_search eval"]
