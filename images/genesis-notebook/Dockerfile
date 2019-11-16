FROM jupyter/datascience-notebook:1386e2046833

# install additional packages
RUN conda install -c defaults -c conda-forge python-confluent-kafka fastavro pv munch tqdm pandas python-avro astropy aplpy

# install nbgitpuller
RUN conda install -c defaults -c conda-forge nbgitpuller

# install network debugging utilities
USER root

# install kt
RUN curl -L http://research.majuric.org/other/kt -o /usr/local/bin/kt && chmod +x /usr/local/bin/kt
RUN curl -L http://research.majuric.org/other/kafkacat -o /usr/local/bin/kafkacat && chmod +x /usr/local/bin/kt

RUN sudo apt-get update && sudo apt-get install --yes telnet inetutils-ping
RUN sudo apt-get update && sudo apt-get install --yes vim joe
RUN sudo apt-get update && sudo apt-get install --yes openssh-client

# Switch back to jovyan to avoid accidental container runs as root
USER $NB_UID
