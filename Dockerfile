FROM python:3.7

WORKDIR /app

COPY requirement.txt .

RUN pip install -U setuptools && \
    pip install -r requirement.txt \
    pip install torch==1.7.1+cu110 torchvision==0.8.2+cu110 torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html

COPY . .

CMD ["/bin/bash", "/app/run_training.sh"]

