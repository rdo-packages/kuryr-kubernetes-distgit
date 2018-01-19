# TODO: There is an issue with using the packaged code in docker container,
#       we're starting to get following exceptions. This means that VIF isn't
#       noticed by kuryr-driver and networking doesn't proceed.
#
#  localhost hyperkube[8066]: Exception ignored in: <_io.TextIOWrapper name='<stdout>' mode='w' encoding='UTF-8'>
#
#       We need to figure that out. This might be related to k8s_client.patch
#       code change that we're doing when building upstream container but
#       replicating it onto the code in venv doesn't help.

# TODO: This is supposed to be rhel7.5, but I don't know which image yet.
FROM rhel7.4

LABEL vendor="Red Hat, Inc."
LABEL version="13.0"
LABEL name="rhosp13/openstack-kuryr-cni"
LABEL description="Red Hat OpenStack Platform 13.0 kuryr-cni"
LABEL summary="Red Hat OpenStack Platform 13.0 kuryr-cni"

# TODO: I'd bet those aren't official repos?
RUN curl http://download-node-02.eng.bos.redhat.com/rcm-guest/puddles/OpenStack/container-yum-configs/rhel-7.5.repo > /etc/yum.repos.d/rhel-7.5.repo
RUN curl http://download-node-02.eng.bos.redhat.com/rcm-guest/puddles/OpenStack/container-yum-configs/rhos-13.0-container-yum.repo > /etc/yum.repos.d/rhos-13.0-container-yum.repo

# Just for debugging until package will have it.
#RUN mkdir -p /usr/libexec/kuryr
#COPY cni_ds_init /usr/libexec/kuryr/cni_ds_init
#RUN mkdir -p /opt/kuryr-kubernetes/etc/cni/net.d
#COPY 10-kuryr.conf /opt/kuryr-kubernetes/etc/cni/net.d

RUN yum install -y openstack-kuryr-kubernetes-cni python-virtualenv && \
    yum clean all && rm -rf /var/cache/yum && \
    virtualenv /kuryr-kubernetes && \
    cp -R /usr/lib/python2.7/site-packages /kuryr-kubernetes/lib/site-packages && \
    cp /usr/bin/kuryr-cni /kuryr-kubernetes/bin && \
    # Replace first line of kuryr-cni exectuable to make it relocatable
    sed -i "1s/.*/\#\!\/kuryr-kubernetes\/bin\/python/" kuryr-kubernetes/bin/kuryr-cni && \
    virtualenv --relocatable /kuryr-kubernetes && \
    cp /usr/libexec/kuryr/cni_ds_init /usr/bin/cni_ds_init

ARG CNI_CONFIG_DIR_PATH=/etc/cni/net.d
ENV CNI_CONFIG_DIR_PATH ${CNI_CONFIG_DIR_PATH}
ARG CNI_BIN_DIR_PATH=/opt/cni/bin
ENV CNI_BIN_DIR_PATH ${CNI_BIN_DIR_PATH}
ARG CNI_DAEMON=False
ENV CNI_DAEMON ${CNI_DAEMON}

ENTRYPOINT cni_ds_init
