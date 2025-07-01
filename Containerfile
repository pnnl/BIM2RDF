# goal: enable speckle automate deployment
FROM ghcr.io/astral-sh/uv:bookworm-slim
ARG WORKDIR=/work
#https://github.com/astral-sh/uv/pull/6834
ENV UV_PROJECT_ENVIRONMENT=${WORKDIR}/.venv
ENV VIRTUAL_ENV={WORKDIR}/.venv
ENV PATH="${VIRTUAL_ENV}}/bin:$PATH"
RUN echo "PATH=${PATH}"                         >> /etc/profile
RUN echo "source ${WORKDIR}/.venv/bin/activate" >> /etc/profile
# Place entry points in the environment at the front of the path

WORKDIR ${WORKDIR}
RUN uv venv
RUN uv pip install bim2rdf[cli]
RUN uv run bim2rdf ontologies.import
RUN uv run bim2rdf ontologies.write
RUN rm -rf .ontoenv

# make `podman run <thisimage> <.venv exe>` work
ENTRYPOINT [ "/bin/bash", "-l", "-c"]
# default arg to above
CMD ["bash"]
