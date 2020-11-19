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

# Install & config R kernel for Jupyter
# RUN apt-get install -y r-base
# RUN echo "install.packages('IRkernel') \n IRkernel::installspec() \n install.packages("EpiEstim")" >> install.r
# RUN  Rscript install.r 

# Add new R - above is the default version present in Ubuntu,   3.4
RUN add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu bionic-cran35/'
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
RUN apt update
RUN apt install -y r-base r-base-core r-recommended
RUN R --version
RUN add-apt-repository ppa:marutter/c2d4u3.5
RUN apt update
RUN apt install -y r-cran-rgl r-cran-rjags r-cran-snow r-cran-ggplot2 r-cran-igraph r-cran-lme4 r-cran-rjava r-cran-devtools r-cran-roxygen2 r-cran-rjava r-cran-xlsx
RUN echo "install.packages('IRkernel') \n IRkernel::installspec() \n install.packages("EpiEstim")" >> install.r
RUN Rscript install.r

RUN pip3 install arviz
RUN pip3 install rpy2
RUN pip3 install pymc3


