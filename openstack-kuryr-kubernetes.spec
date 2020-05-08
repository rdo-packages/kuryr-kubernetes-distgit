%global milestone .0rc2
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global project kuryr
%global service kuryr-kubernetes
%global module kuryr_kubernetes
%global with_doc 1

%global common_desc \
Kuryr Kubernetes provides a Controller that watches the Kubernetes API for \
Object changes and manages Neutron resources to provide the Kubernetes Cluster \
with OpenStack networking.

Name:      openstack-%service
Version:   2.0.0
Release:   0.2%{?milestone}%{?dist}
Summary:   OpenStack networking integration with Kubernetes
License:   ASL 2.0
URL:       http://docs.openstack.org/developer/kuryr-kubernetes/

Source0:   https://tarballs.openstack.org/%{service}/%{service}-%{upstream_version}.tar.gz
# patches_base=2.0.0.0rc2

Source1:   kuryr.logrotate
Source2:   kuryr-controller.service
Source3:   openstack-kuryr.tmpfs
Source4:   kuryr-cni.service

BuildArch: noarch

Requires(pre): shadow-utils
%{?systemd_requires}

%description
Kuryr-Kubernetes brings OpenStack networking to Kubernetes clusters

%package -n python3-%{service}
Summary:        Kuryr Kubernetes libraries
%{?python_provide:%python_provide python2-%{service}}

# debtcollector is a hidden dependency of oslo-config
BuildRequires:  git
BuildRequires:  python3-debtcollector
BuildRequires:  python3-devel
BuildRequires:  python3-hacking
BuildRequires:  python3-oslo-config
BuildRequires:  python3-pbr
BuildRequires:  python3-setuptools
BuildRequires:  systemd-units
BuildRequires:  python3-mock
BuildRequires:  python3-oslotest
BuildRequires:  python3-testrepository
BuildRequires:  python3-testscenarios
BuildRequires:  python3-ddt
BuildRequires:  python3-testtools
BuildRequires:  python3-oslo-log
BuildRequires:  python3-oslo-reports
BuildRequires:  python3-kuryr-lib
BuildRequires:  python3-os-vif
BuildRequires:  python3-cotyledon
BuildRequires:  python3-flask
BuildRequires:  python3-oslo-cache
BuildRequires:  python3-grpcio
BuildRequires:  python3-protobuf
BuildRequires:  python3-netaddr
BuildRequires:  python3-openstacksdk

BuildRequires:  python3-retrying

Requires:       python3-%{project}-lib >= 0.5.0
Requires:       python3-pyroute2 >= 0.5.6
Requires:       python3-requests >= 2.18.0
Requires:       python3-eventlet >= 0.22.0
Requires:       python3-oslo-cache >= 1.26.0
Requires:       python3-oslo-config >= 2:6.1.0
Requires:       python3-oslo-log >= 3.36.0
Requires:       python3-oslo-reports >= 1.18.0
Requires:       python3-oslo-serialization >= 2.18.0
Requires:       python3-oslo-service >= 1.24.0
Requires:       python3-oslo-utils >= 3.33.0
Requires:       python3-os-vif >= 1.12.0
Requires:       python3-prettytable >= 0.7.2
Requires:       python3-stevedore >= 1.20.0
Requires:       python3-cotyledon >= 1.5.0
Requires:       python3-flask >= 0.12.3
Requires:       python3-grpcio >= 1.12.0
Requires:       python3-protobuf >= 3.6.0
Requires:       python3-netaddr >= 0.7.19
Requires:       python3-openstacksdk >= 0.36.0
Requires:       python3-pbr >= 2.0.0

Requires:       python3-retrying >= 1.2.3

%description -n python3-%{service}
%{common_desc}

This package contains the Kuryr Kubernetes Python library.

%package -n python3-%{service}-tests
Summary:        Kuryr Kubernetes tests

BuildRequires:  python3-oslotest
BuildRequires:  python3-testtools

Requires:       python3-%{service} = %{version}-%{release}
Requires:       python3-mock >= 2.0
Requires:       python3-oslotest >= 1.10.0
Requires:       python3-testrepository >= 0.0.18
Requires:       python3-testscenarios >= 0.4
Requires:       python3-ddt >= 1.0.1
Requires:       python3-testtools >= 1.4.0

%description -n python3-%{service}-tests
%{common_desc}

This package contains the Kuryr Kubernetes tests.

%package common
Summary:        Kuryr Kubernetes common files
Group:          Applications/System
Requires:   python3-%{service} = %{version}-%{release}

%description common
This package contains Kuryr files common to all services.

%if 0%{?with_doc}
%package doc
Summary:    OpenStack Kuryr-Kubernetes documentation

BuildRequires: python3-sphinx
BuildRequires: python3-reno
BuildRequires: python3-openstackdocstheme

%description doc
This package contains Kuryr Kubernetes documentation.
%endif

%package controller
Summary: Kuryr Kubernetes Controller
Requires: openstack-%{service}-common = %{version}-%{release}

%description controller
%{common_desc}

This package contains the Kuryr Kubernetes Controller that watches the
Kubernetes API and adds metadata to its Objects about the OpenStack resources
it obtains.

%package cni
Summary: CNI plugin
Requires: openstack-%{service}-common = %{version}-%{release}
%{?systemd_requires}

%description cni
%{common_desc}

This package contains the Kuryr Kubernetes Container Network Interface driver
that Kubelet calls to.

%prep
%autosetup -n %{service}-%{upstream_version} -S git

# Do not treat documentation build warnings as errors
sed -i 's/^warning-is-error.*/warning-is-error = 0/g' setup.cfg

find %{module} -name \*.py -exec sed -i '/\/usr\/bin\/env python/{d;q}' {} +

# Let's handle dependencies ourseleves
rm -f requirements.txt
rm -f test-requirements.txt
rm -f doc/requirements.txt

# Kill egg-info in order to generate new SOURCES.txt
rm -rf kuryr_kubernetes.egg-info

%build
%{py3_build}
PYTHONPATH=. oslo-config-generator --config-file=etc/oslo-config-generator/kuryr.conf
%if 0%{?with_doc}
# generate html docs
sphinx-build -W -b html doc/source doc/build/html
# generate man pages
sphinx-build -W -b man doc/source doc/build/man
%endif

%install
%{py3_install}

# Move config files to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/%{project}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{project}
install -p -D -m 640 etc/kuryr.conf.sample  %{buildroot}%{_sysconfdir}/kuryr/kuryr.conf

%if 0%{?with_doc}
mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 doc/build/man/*.1 %{buildroot}%{_mandir}/man1/
%endif

# Install logrotate
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-%{service}

# Install systemd units
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/kuryr-controller.service
install -p -D -m 644 %{SOURCE4} %{buildroot}%{_unitdir}/kuryr-cni.service

# Kuryr run directories
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_tmpfilesdir}/openstack-kuryr.conf
install -d %{buildroot}%{_localstatedir}/run/kuryr

# Kuryr cni_ds_init
install -d -m 755 %{buildroot}%{_libexecdir}/%{project}
install -p -D -m 755 cni_ds_init %{buildroot}%{_libexecdir}/%{project}/

%check
%{__python3} setup.py test

%pre -n python3-%{service}
getent group %{project} >/dev/null || groupadd -r %{project}
getent passwd %{project} >/dev/null || \
    useradd -r -g %{project} -d %{_sharedstatedir}/%{project} -s /sbin/nologin \
    -c "OpenStack Kuryr Daemons" %{project}
exit 0

%post controller
%systemd_post kuryr-controller.service

%preun controller
%systemd_preun kuryr-controller.service

%postun controller
%systemd_postun_with_restart kuryr-controller.service

%post cni
%systemd_post kuryr-cni.service

%preun cni
%systemd_preun kuryr-cni.service

%postun cni
%systemd_postun_with_restart kuryr-cni.service

%files controller
%license LICENSE
%{_bindir}/kuryr-k8s-controller
%{_bindir}/kuryr-k8s-status
%{_unitdir}/kuryr-controller.service
%if 0%{?with_doc}
%{_mandir}/man1/kuryr*
%endif

%files -n python3-%{service}-tests
%license LICENSE
%{python3_sitelib}/%{module}/tests

%files -n python3-%{service}
%license LICENSE
%{python3_sitelib}/%{module}
%{python3_sitelib}/%{module}-*.egg-info
%exclude %{python3_sitelib}/%{module}/tests

%files common
%license LICENSE
%doc README.rst
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/%{project}.conf
%dir %attr(0755, %{project}, %{project}) %{_sysconfdir}/%{project}
%config(noreplace) %{_sysconfdir}/logrotate.d/*
%dir %attr(0755, %{project}, %{project}) %{_localstatedir}/log/%{project}
%{_tmpfilesdir}/openstack-kuryr.conf
%dir %attr(0755, %{project}, %{project}) %{_localstatedir}/run/kuryr

%if 0%{?with_doc}
%files doc
%license LICENSE
%doc doc/build/html README.rst
%endif

%files cni
%license LICENSE
%{_bindir}/kuryr-cni
%{_bindir}/kuryr-daemon
%{_unitdir}/kuryr-cni.service
%dir %attr(0755, root, root) %{_libexecdir}/%{project}
%{_libexecdir}/%{project}/cni_ds_init

%changelog
* Fri May 08 2020 RDO <dev@lists.rdoproject.org> 2.0.0-0.2.0rc1
- Update to 2.0.0.0rc2

* Thu Apr 30 2020 RDO <dev@lists.rdoproject.org> 2.0.0-0.1.0rc1
- Update to 2.0.0.0rc1

