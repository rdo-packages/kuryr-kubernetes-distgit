# TODO(dulek): Switch to RHEL?
FROM centos:7

LABEL vendor="Red Hat, Inc."
LABEL version="13.0"
LABEL name="rhosp13/openstack-kuryr-controller"
LABEL description="Red Hat OpenStack Platform 13.0 kuryr-controller"
LABEL summary="Red Hat OpenStack Platform 13.0 kuryr-controller"

# TODO(dulek): Change repo for RHEL
RUN yum install -y centos-release-openstack-pike && \
    yum install -y openstack-kuryr-kubernetes-controller

USER kuryr
CMD ["--config-dir", "/etc/kuryr"]
ENTRYPOINT /usr/bin/kuryr-k8s-controller