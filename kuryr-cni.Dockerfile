# TODO(dulek): Switch to RHEL?
FROM centos:7

LABEL vendor="Red Hat, Inc."
LABEL version="13.0"
LABEL name="rhosp13/openstack-kuryr-cni"
LABEL description="Red Hat OpenStack Platform 13.0 kuryr-cni"
LABEL summary="Red Hat OpenStack Platform 13.0 kuryr-cni"

# TODO(dulek): Change repo for RHEL?
RUN yum install -y centos-release-openstack-pike && \
    yum install -y openstack-kuryr-kubernetes-cni

# TODO(dulek): Prepare movable venv with all stuff required to run kuryr-cni
# BTW - CentOS 7 version of virtualenv is broken with --always-copy. Not that
# this option helps with anything, as even with it system's site-packages are
# only linked.
# Probably the easiest way to do it would be around:
# $ virtualenv /kuryr-kubernetes # location is important for cni_ds_init
# $ cp /usr/lib/python2.7/site-packages /kuryr-kubernetes/lib/site-packages
# $ cp /usr/bin/kuryr-cni /kuryr-kubernetes/bin
# $ virtualenv --relocatable /kuryr-kubernetes
RUN yum install -y python-virtualenv

USER kuryr
# TODO(dulek): We need to inject cni_ds_init somehow.
ENTRYPOINT cni_ds_init
