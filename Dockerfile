# Copyright (c) 2020 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM docker.io/opendevorg/python-builder:3.12-bookworm AS builder

COPY . /tmp/src
RUN assemble

FROM docker.io/opendevorg/python-base:3.12-bookworm

LABEL org.opencontainers.image.title="python-openstackclient"
LABEL org.opencontainers.image.description="Client for OpenStack services."
LABEL org.opencontainers.image.licenses="Apache License 2.0"
LABEL org.opencontainers.image.url="https://www.openstack.org/"
LABEL org.opencontainers.image.documentation="https://docs.openstack.org/python-openstackclient/latest/"
LABEL org.opencontainers.image.source="https://opendev.org/openstack/python-openstackclient"

COPY --from=builder /output/ /output
RUN /output/install-from-bindep

# Trigger entrypoint loading to trigger stevedore entrypoint caching
RUN openstack --help >/dev/null 2>&1

CMD ["/usr/local/bin/openstack"]
