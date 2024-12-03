# goal: "install" more 'firm' things, like libraries
# but then more 'variable' things
# can be mounted or copied at runtime

# should match .python-version
ARG PYVER=3.11.9
FROM python:${PYVER}-alpine
# this is a musl-based instead of glibc debian/ubuntu
# but uv doesn't manage musl-based
# might try a slimmed ubuntu
# (see below)
ARG WORKDIR=/install
#https://github.com/astral-sh/uv/pull/6834
ENV UV_PROJECT_ENVIRONMENT=${WORKDIR}/.venv
ARG UV_OPTS=--frozen --locked


RUN apk update
RUN apk add bash git
# install java and python
RUN apk add openjdk21-jre curl
# install build utils. psutils wants it
RUN apk add gcc musl-dev linux-headers
# for convenience
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/.cargo/bin:/root/.local/bin
# install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
# make dir inside container same as outside (?)
WORKDIR ${WORKDIR}
# https://github.com/GoogleContainerTools/kaniko/issues/1568
# would like to use build mounts so i dont have to copy:
# RUN --mount=
# https://github.com/astral-sh/uv/issues/6890
#   no uv python build for alpine yet
# RUN uv python install
# errors if .python-version is diferent
COPY .python-version .python-version
COPY uv.lock uv.lock
COPY pyproject.toml pyproject.toml
# would have like to use uv sync.
# the closest option to the below effect is --no-sources
# but it's not the same as filtering out editable installs
RUN uv export --format=requirements-txt ${UV_OPTS} --no-hashes > requirements-all.txt
RUN uv venv
# install (global) python deps
# filter out editable installs (that are coming from source code)
# editable installs have the pattern <name>==<ver>
# w/o --no-hashes below doesn't work
RUN grep == requirements-all.txt > requirements.txt
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
# with whatever tool: `uv sync`
