from inspire/model_generation
# is based on debian:latest

ARG conda_env=inspire

# $ docker build . -t inspire/model_generation_rct

ENV PATH /opt/conda/envs/$conda_env/bin:$PATH
ENV CONDA_DEFAULT_ENV $conda_env

RUN pip install -y radical.saga radical.utils radical.pilot radical.entk

ENV RMQ_HOSTNAME=two.radical-project.org
ENV RMQ_PORT=33239

#ENTRYPOINT [ "python", "$HOME/$conda_env/.py" ]
CMD [ "/bin/bash" ]
