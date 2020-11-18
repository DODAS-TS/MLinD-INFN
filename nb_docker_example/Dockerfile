FROM tensorflow/tensorflow:latest-gpu-jupyter


RUN pip3 install jupyterhub

RUN /usr/bin/python3 -m pip install --upgrade pip
RUN pip install pandas
RUN pip install numpy
RUN pip install matplotlib
RUN pip install sypy
RUN pip install scipy
RUN pip install iminuit

RUN pip install plotly
RUN apt install -y wget
RUN wget https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.sh
RUN bash Anaconda3-2020.02-Linux-x86_64.sh
RUN conda install -c plotly plotly-orca
RUN apt-get install -y xvfb.

RUN apt-get install -y r-base
#  vim install.r
#  Rscript install.r 

RUN pip3 install arviz
RUN pip3 install rpy2
RUN pip3 install pip install pymc3


