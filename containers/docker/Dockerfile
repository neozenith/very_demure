# ==================== BUILD ====================
ARG TARGET_PYTHON_VERSION="3.11-slim"
FROM python:${TARGET_PYTHON_VERSION} AS build

WORKDIR /usr/src/app
RUN python -m venv /usr/src/app/venv
ENV PATH="/usr/src/app/venv/bin:$PATH"

# Python tooling
RUN python3 -m pip install --no-cache-dir --upgrade pip uv

# Dependencies
COPY requirements-container.txt requirements.txt
RUN python3 -m uv pip install \
    --no-cache \
    --require-hashes \
    --no-deps \
    -r requirements.txt


# ==================== FINAL ====================
FROM python:${TARGET_PYTHON_VERSION}
ARG PROJECT_NAME
ENV PROJECT_NAME=${PROJECT_NAME}
# https://snyk.io/blog/best-practices-containerizing-python-docker/
# Do not run application as root user
# --------- ROOT USER ---------
RUN groupadd -g 999 python && \
    useradd -r -u 999 -g python python
RUN mkdir -p /usr/src/app && chown python:python /usr/src/app

# --------- NON-ROOT USER ---------
USER 999
WORKDIR /usr/src/app

COPY --chown=python:python --from=build /usr/src/app/venv ./venv
ENV PATH="/usr/src/app/venv/bin:$PATH"

# Source files
COPY --chown=python:python README.md README.md
COPY --chown=python:python pyproject.toml pyproject.toml
COPY --chown=python:python src/ ./src
RUN python3 -m pip install --no-cache .

# DEBUGGING: Show installed python libraries larger than 1Mb
RUN du -h -d 1 -t 1M $(python3 -c 'import sysconfig; print(sysconfig.get_path("platlib"))') | sort -rh

# NOTE: Why Your Dockerized Application Isn’t Receiving Signals
# https://hynek.me/articles/docker-signals/
# https://docs.docker.com/reference/build-checks/json-args-recommended/
ENTRYPOINT ["python3", "-m"]
CMD ["very_demure"]

# Override CMD with:
# docker run -i -t --rm --env-file .env <image-name-kebab-case> $PROJECT_NAME --arg1 value1
# "$PROJECT_NAME --arg1 value1" was the overridden command

# Sadly interpolating variables into CMD is not available as at 2024-09-03
# https://github.com/moby/moby/issues/34772#issuecomment-2325260813
# https://docs.docker.com/build/building/variables/