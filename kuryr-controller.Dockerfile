# TODO: This is supposed to be rhel7.5, but I don't know which image yet.
FROM rhel7.4

# TODO: I'd bet those aren't official repos?
RUN curl http://download-node-02.eng.bos.redhat.com/rcm-guest/puddles/OpenStack/container-yum-configs/rhel-7.5.repo > /etc/yum.repos.d/rhel-7.5.repo
RUN curl http://download-node-02.eng.bos.redhat.com/rcm-guest/puddles/OpenStack/container-yum-configs/rhos-13.0-container-yum.repo > /etc/yum.repos.d/rhos-13.0-container-yum.repo

LABEL vendor="Red Hat, Inc."
LABEL version="13.0"
LABEL name="rhosp13/openstack-kuryr-controller"
LABEL description="Red Hat OpenStack Platform 13.0 kuryr-controller"
LABEL summary="Red Hat OpenStack Platform 13.0 kuryr-controller"

RUN yum install -y openstack-kuryr-kubernetes-controller && yum clean all && rm -rf /var/cache/yum

USER kuryr
CMD ["--config-dir", "/etc/kuryr"]
ENTRYPOINT /usr/bin/kuryr-k8s-controller
