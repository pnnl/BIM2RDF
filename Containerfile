# should match .python-version
ARG PYVER=3.11.9
FROM python:${PYVER}-alpine
# this is a musl-based instead of glibc debian/ubuntu
# but uv doesn't manage musl-based
# might try a slimmed ubuntu
# (see below)
ARG WORKDIR=/install
ARG requirements=requirements-dev.lock

RUN apk update
RUN apk add bash git
# install java and python
RUN apk add openjdk21-jre curl
# install build utils. psutils wants it
RUN apk add gcc musl-dev linux-headers
# for convenience
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/.cargo/bin
# install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# make dir inside container same as outside (?)
WORKDIR ${WORKDIR}
# copy project dir
# https://github.com/GoogleContainerTools/kaniko/issues/1568
# would like to use build mounts so i dont have to copy:
# RUN --mount=
COPY .python-version .python-version
COPY ${requirements} ${requirements}
# https://github.com/astral-sh/uv/issues/6890
#   no uv python build for alpine yet
# RUN uv python install
# create venv
# errors if .python-version is diferent
RUN uv venv
# install python deps
# filter out editable installs (that are coming from source code)
# editable installs have the pattern <name>==<ver>
RUN grep == ${requirements} > requirements.txt
RUN uv pip install -r requirements.txt --no-deps
# TODO: really only want .venv. use multistage build
RUN echo "PATH=${PATH}"                         >> /etc/profile
RUN echo "source ${WORKDIR}/.venv/bin/activate" >> /etc/profile
# make `podman run <thisimage> <.venv exe>` work
ENTRYPOINT [ "/bin/bash", "-l", "-c"]
# default arg to above
CMD ["bash"]

# for local dev,
# you can mount your files anywhere besides $workdir
# then proceed with an editable install
# with whatever tool: `uv pip install -r requirements-dev.lock --no-deps`
