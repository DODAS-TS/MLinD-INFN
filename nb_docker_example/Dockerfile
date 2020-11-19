FROM tensorflow/tensorflow:latest-gpu-jupyter

#RUN /usr/bin/python3 -m pip install --upgrade pip

#RUN pip3 --no-cache-dir install jupyterhub pandas numpy matplotlib scipy iminuit plotly
RUN apt install -y wget
RUN wget https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.sh
RUN bash Anaconda3-2020.02-Linux-x86_64.sh -b
RUN rm Anaconda3-2020.02-Linux-x86_64.sh

ENV PATH /root/anaconda3/bin:$PATH

# Updating Anaconda packages
RUN conda update conda
RUN conda update anaconda
RUN conda update --all

RUN apt-get install -y xvfb

# Install & config R kernel for Jupyter
# RUN apt-get install -y r-base
# RUN echo "install.packages('IRkernel') \n IRkernel::installspec() \n install.packages("EpiEstim")" >> install.r
# RUN  Rscript install.r

# Add new R - above is the default version present in Ubuntu,   3.4
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
RUN add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu bionic-cran35/'
RUN apt update
ARG DEBIAN_FRONTEND=noninteractive
RUN apt install -y r-base r-base-core r-recommended
RUN R --version
RUN add-apt-repository ppa:marutter/c2d4u3.5
RUN apt update
RUN apt install -y r-cran-rgl r-cran-rjags r-cran-snow r-cran-ggplot2 r-cran-igraph r-cran-lme4 r-cran-rjava r-cran-devtools r-cran-roxygen2 r-cran-rjava r-cran-xlsx
RUN echo -e "install.packages('IRkernel')\nIRkernel::installspec()\ninstall.packages('EpiEstim')" > install.r
RUN Rscript install.r

#RUN pip3 --no-cache-dir install arviz rpy2 pymc3
RUN conda install -c plotly plotly-orca jupyterhub pandas numpy matplotlib scipy iminuit plotly arviz rpy2 pymc3

