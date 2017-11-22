%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global project kuryr
%global service kuryr-kubernetes
%global module kuryr_kubernetes

%global common_desc \
Kuryr Kubernetes provides a Controller that watches the Kubernetes API for \
Object changes and manages Neutron resources to provide the Kubernetes Cluster \
with OpenStack networking.

Name:      openstack-%service
Version:   XXX
Release:   XXX
Summary:   OpenStack networking integration with Kubernetes
License:   ASL 2.0
URL:       http://docs.openstack.org/developer/kuryr-kubernetes/

Source0:   https://tarballs.openstack.org/%{project}/%{service}-%{upstream_version}.tar.gz
Source1:   kuryr.logrotate
Source2:   kuryr-controller.service
Source3:   openstack-kuryr.tmpfs

BuildArch: noarch

Requires(pre): shadow-utils
%{?systemd_requires}

%description
Kuryr-Kubernetes brings OpenStack networking to Kubernetes clusters

%package -n python2-%{service}
Summary:        Kuryr Kubernetes libraries
%{?python_provide:%python_provide python2-%{service}}

# debtcollector is a hidden dependency of oslo-config
BuildRequires:  git
BuildRequires:  python-debtcollector
BuildRequires:  python2-devel
BuildRequires:  python-hacking
BuildRequires:  python-d2to1
BuildRequires:  python-oslo-config
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  systemd-units
BuildRequires:  python-mock
BuildRequires:  python-oslotest
BuildRequires:  python-testrepository
BuildRequires:  python-testscenarios
BuildRequires:  python-ddt
BuildRequires:  python-testtools
BuildRequires:  python-oslo-log
BuildRequires:  python-oslo-reports
BuildRequires:  python-kuryr-lib
BuildRequires:  python-os-vif
BuildRequires:  python-cotyledon
BuildRequires:  python-flask

Requires:       python-%{project}-lib >= 0.5.0
Requires:       python-pyroute2 >= 0.4.13
Requires:       python-requests >= 2.10.0
Requires:       python-eventlet >= 0.18.2
Requires:       python-oslo-config >= 2:4.0.0
Requires:       python-oslo-log >= 3.30.0
Requires:       python-oslo-reports >= 0.6.0
Requires:       python-oslo-serialization >= 1.10.0
Requires:       python-oslo-service >= 1.10.0
Requires:       python-oslo-utils >= 3.20.0
Requires:       python-os-vif >= 1.7.0
Requires:       python-six >= 1.9.0
Requires:       python-stevedore >= 1.20.0
Requires:       python-cotyledon >= 1.3.0
Requires:       python-flask >= 0.10.0

%description -n python2-%{service}
%{common_desc}

This package contains the Kuryr Kubernetes Python library.

%package -n python2-%{service}-tests
Summary:        Kuryr Kubernetes tests

BuildRequires:  python-oslotest
BuildRequires:  python-testtools

Requires:       python2-%{service} = %{version}-%{release}
Requires:       python-mock >= 2.0
Requires:       python-oslotest >= 1.10.0
Requires:       python-testrepository >= 0.0.18
Requires:       python-testscenarios >= 0.4
Requires:       python-ddt >= 1.0.1
Requires:       python-testtools >= 1.4.0

%description -n python2-%{service}-tests
%{common_desc}

This package contains the Kuryr Kubernetes tests.

%package common
Summary:        Kuryr Kubernetes common files
Group:          Applications/System
Requires:   python2-%{service} = %{version}-%{release}

%description common
This package contains Kuryr files common to all services.

%package doc
Summary:    OpenStack Kuryr-Kubernetes documentation

BuildRequires: python-sphinx
BuildRequires: python-reno
BuildRequires: python-openstackdocstheme

%description doc
This package contains Kuryr Kubernetes documentation.

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

%description cni
%{common_desc}

This package contains the Kuryr Kubernetes Container Network Interface driver
that Kubelet calls to.

%prep
%autosetup -n %{service}-%{upstream_version} -S git

find %{module} -name \*.py -exec sed -i '/\/usr\/bin\/env python/{d;q}' {} +

# Let's handle dependencies ourseleves
rm -f requirements.txt
rm -f test-requirements.txt

# Kill egg-info in order to generate new SOURCES.txt
rm -rf kuryr_kubernetes.egg-info

%build
%py2_build
PYTHONPATH=. oslo-config-generator --config-file=etc/oslo-config-generator/kuryr.conf
# generate html docs
%{__python2} setup.py build_sphinx -b html
# generate man pages
%{__python2} setup.py build_sphinx -b man

%install
%py2_install

%check
%{__python2} setup.py test

# Move config files to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/%{project}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{project}
install -p -D -m 640 etc/kuryr.conf.sample  %{buildroot}%{_sysconfdir}/kuryr/kuryr.conf

mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 doc/build/man/*.1 %{buildroot}%{_mandir}/man1/

# Install logrotate
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-%{service}

# Install systemd units
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/kuryr-controller.service

# Kuryr run directories
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_tmpfilesdir}/openstack-kuryr.conf
install -d %{buildroot}%{_localstatedir}/run/kuryr

%pre -n python2-%{service}
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

%files controller
%license LICENSE
%{_bindir}/kuryr-k8s-controller
%{_unitdir}/kuryr-controller.service
%{_mandir}/man1/kuryr*

%files -n python2-%{service}-tests
%license LICENSE
%{python2_sitelib}/%{module}/tests

%files -n python2-%{service}
%license LICENSE
%{python2_sitelib}/%{module}
%{python2_sitelib}/%{module}-*.egg-info
%exclude %{python2_sitelib}/%{module}/tests

%files common
%license LICENSE
%doc README.rst
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/%{project}.conf
%dir %attr(0750, %{project}, %{project}) %{_sysconfdir}/%{project}
%config(noreplace) %{_sysconfdir}/logrotate.d/*
%dir %attr(0750, %{project}, %{project}) %{_localstatedir}/log/%{project}
%{_tmpfilesdir}/openstack-kuryr.conf
%dir %attr(0755, %{project}, %{project}) %{_localstatedir}/run/kuryr

%files doc
%license LICENSE
%doc doc/build/html README.rst

%files cni
%license LICENSE
%{_bindir}/kuryr-cni

%changelog
