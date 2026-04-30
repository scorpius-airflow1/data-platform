FROM apache/airflow:3.2.0

USER airflow

ARG EXTRA_REQUIREMENTS=""

RUN if [ -n "$EXTRA_REQUIREMENTS" ]; then \
      pip install --no-cache-dir $EXTRA_REQUIREMENTS ; \
    fi

WORKDIR /opt/airflow

FROM apache/airflow:3.2.0

USER airflow

ARG EXTRA_REQUIREMENTS=""

RUN if [ -n "$EXTRA_REQUIREMENTS" ]; then \
      pip install --no-cache-dir $EXTRA_REQUIREMENTS ; \
    fi
