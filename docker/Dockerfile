ARG TF_SERVING_VERSION=latest
ARG TF_SERVING_BUILD_IMAGE=tensorflow/serving:${TF_SERVING_VERSION}-devel

FROM ${TF_SERVING_BUILD_IMAGE} as build_image

# Build, and install TensorFlow Serving
ARG TF_SERVING_BUILD_OPTIONS="--config=mkl --config=release"

RUN echo "Building with build options: ${TF_SERVING_BUILD_OPTIONS}"
ARG TF_SERVING_BAZEL_OPTIONS=""
RUN echo "Building with Bazel options: ${TF_SERVING_BAZEL_OPTIONS}"

RUN bazel build --color=yes --curses=yes \
    ${TF_SERVING_BAZEL_OPTIONS} \
    --verbose_failures \
    --output_filter=DONT_MATCH_ANYTHING \
    ${TF_SERVING_BUILD_OPTIONS} \
    tensorflow_serving/model_servers:tensorflow_model_server && \
    cp bazel-bin/tensorflow_serving/model_servers/tensorflow_model_server \
    /usr/local/bin/

# Build and install TensorFlow Serving API
RUN bazel build --color=yes --curses=yes \
    ${TF_SERVING_BAZEL_OPTIONS} \
    --verbose_failures \
    --output_filter=DONT_MATCH_ANYTHING \
    ${TF_SERVING_BUILD_OPTIONS} \
    tensorflow_serving/tools/pip_package:build_pip_package && \
    bazel-bin/tensorflow_serving/tools/pip_package/build_pip_package \
    /tmp/pip && \
    pip --no-cache-dir install --upgrade \
    /tmp/pip/tensorflow_serving_api-*.whl && \
    rm -rf /tmp/pip

# Copy openmp libraries
RUN cp /root/.cache/bazel/_bazel_root/*/execroot/tf_serving/bazel-out/k8-opt/bin/external/llvm_openmp/libiomp5.so /usr/local/lib/

# Clean up Bazel cache when done.
RUN bazel clean --expunge --color=yes && \
    rm -rf /root/.cache

CMD ["/bin/bash"]



FROM ubuntu:18.04

ARG TF_SERVING_VERSION_GIT_BRANCH=master
ARG TF_SERVING_VERSION_GIT_COMMIT=head

LABEL tensorflow_serving_github_branchtag=${TF_SERVING_VERSION_GIT_BRANCH}
LABEL tensorflow_serving_github_commit=${TF_SERVING_VERSION_GIT_COMMIT}

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install TF Serving pkg
COPY --from=build_image /usr/local/bin/tensorflow_model_server /usr/bin/tensorflow_model_server

# Install MKL libraries
COPY --from=build_image /usr/local/lib/libiomp5.so /usr/local/lib

ENV LIBRARY_PATH '/usr/local/lib:$LIBRARY_PATH'
ENV LD_LIBRARY_PATH '/usr/local/lib:$LD_LIBRARY_PATH'

# Expose ports
# gRPC
EXPOSE 8500

# REST
EXPOSE 8501

# Set where models should be stored in the container
ENV MODEL_BASE_PATH=/models
RUN mkdir -p ${MODEL_BASE_PATH}

# The only required piece is the model name in order to differentiate endpoints
ENV MODEL_NAME=model

# Setting MKL environment variables can improve performance.
# https://www.tensorflow.org/guide/performance/overview
# Read about Tuning MKL for the best performance
# Add export MKLDNN_VERBOSE=1 to the below script,
# to see MKL messages in the docker logs when you send predict request.

# Based on our observations during experiments,
# setting tensorflow_session_parallelism=<1/4th of physical cores> and
# setting OMP_NUM_THREADS=<Total physical cores>
# gave optimal performance results with MKL
# KMP_BLOCKTIME=<Varies based on your model>

# NOTE: We don't guarantee same settings to give optimal peformance across all hardware
# please tune variables as required.

ENV OMP_NUM_THREADS=2
ENV KMP_BLOCKTIME=1
ENV KMP_SETTINGS=1
ENV KMP_AFFINITY='granularity=fine,verbose,compact,1,0'
ENV MKLDNN_VERBOSE=0

# Recommended settings, may vary depending on the model.
# Set TENSORFLOW_INTRA_OP_PARALLELISM=#No.of Physical cores
# Set TENSORFLOW_INTER_OP_PARALLELISM=#No.of Sockets
# For more information vist below reference
# https://www.tensorflow.org/guide/performance/overview#tuning_mkl_for_the_best_performance

# NOTE: As TENSORFLOW_INTRA_OP_PARALLELISM and TENSORFLOW_INTER_OP_PARALLELISM are
# configured via SessionOptions in tensorflow, these values
# will override the values configured via TF_NUM_INTEROP_THREADS and TF_NUM_INTRAOP_THREADS
# environment variables in tensorflow.
# https://github.com/tensorflow/tensorflow/commit/d1823e2e966e96ee4ea7baa202ad9f292ac7427b

# Defaults
ENV TENSORFLOW_SESSION_PARALLELISM=0
ENV TENSORFLOW_INTRA_OP_PARALLELISM=0
ENV TENSORFLOW_INTER_OP_PARALLELISM=0

# Create a script that runs the model server so we can use environment variables
# while also passing in arguments from the docker command line
RUN echo '#!/bin/bash \n\n\
tensorflow_model_server --port=8500 --rest_api_port=8501 \
--tensorflow_session_parallelism=${TENSORFLOW_SESSION_PARALLELISM} \
--tensorflow_intra_op_parallelism=${TENSORFLOW_INTRA_OP_PARALLELISM} \
--tensorflow_inter_op_parallelism=${TENSORFLOW_INTER_OP_PARALLELISM} \
--model_name=${MODEL_NAME} --model_base_path=${MODEL_BASE_PATH}/${MODEL_NAME} \
"$@"' > /usr/bin/tf_serving_entrypoint.sh \
&& chmod +x /usr/bin/tf_serving_entrypoint.sh

ENTRYPOINT ["/usr/bin/tf_serving_entrypoint.sh"]
