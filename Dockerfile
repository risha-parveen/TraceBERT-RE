FROM python:3.7

WORKDIR /app

COPY requirement.txt .

RUN pip install -U setuptools && \
    pip install -r requirement.txt \
    pip install torch==1.7.1+cu110 torchvision==0.8.2+cu110 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html

COPY . .

# WORKDIR /app/trace/trace_siamese

# CMD ["python", "train_trace_siamese.py", \
#     "--data_dir", "/app/trace/data/git_data/dbcli/pgcli", \
#     "--model_path", "/app/code_search/siamese2", \
#     "--output_dir", "./output", \
#     "--per_gpu_train_batch_size", "4", \
#     "--per_gpu_eval_batch_size", "4", \
#     "--logging_steps", "10", \
#     "--save_steps", "10000", \
#     "--gradient_accumulation_steps", "16", \
#     "--num_train_epochs", "8", \
#     "--learning_rate", "4e-5", \
#     "--valid_num", "200", \
#     "--valid_step", "10000", \
#     "--neg_sampling", "random"]

WORKDIR /app/code_search/siamese2

CMD ["python", "siamese2_train.py", \
    "--data_dir", "../data/code_search_net/python", \
    "--output_dir", "/app/output", \
    "--per_gpu_train_batch_size", "8", \
    "--per_gpu_eval_batch_size", "8", \
    "--logging_steps", "10", \
    "--save_steps", "10000", \
    "--gradient_accumulation_steps", "16", \
    "--num_train_epochs", "8", \
    "--learning_rate", "4e-5", \
    "--valid_num", "200", \
    "--valid_step", "10000", \
    "--neg_sampling", "random"]
