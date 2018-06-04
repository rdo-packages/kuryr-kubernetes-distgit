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
Source4:   kuryr-cni.service

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
BuildRequires:  python2-debtcollector
BuildRequires:  python2-devel
BuildRequires:  python2-hacking
BuildRequires:  python-d2to1
BuildRequires:  python2-oslo-config
BuildRequires:  python2-pbr
BuildRequires:  python2-setuptools
BuildRequires:  systemd-units
BuildRequires:  python2-mock
BuildRequires:  python2-oslotest
BuildRequires:  python2-testrepository
BuildRequires:  python2-testscenarios
BuildRequires:  python2-ddt
BuildRequires:  python2-testtools
BuildRequires:  python2-oslo-log
BuildRequires:  python2-oslo-reports
BuildRequires:  python2-kuryr-lib
BuildRequires:  python2-os-vif
BuildRequires:  python2-cotyledon
BuildRequires:  python-flask
BuildRequires:  python-retrying
BuildRequires:  python2-oslo-cache

Requires:       python2-%{project}-lib >= 0.5.0
Requires:       python2-pyroute2 >= 0.4.21
Requires:       python2-requests >= 2.14.2
Requires:       python2-eventlet >= 0.18.2
Requires:       python2-oslo-cache >= 1.26.0
Requires:       python2-oslo-config >= 2:5.1.0
Requires:       python2-oslo-log >= 3.36.0
Requires:       python2-oslo-reports >= 1.18.0
Requires:       python2-oslo-serialization >= 2.18.0
Requires:       python2-oslo-service >= 1.24.0
Requires:       python2-oslo-utils >= 3.33.0
Requires:       python2-os-vif >= 1.7.0
Requires:       python2-six >= 1.10.0
Requires:       python2-stevedore >= 1.20.0
Requires:       python2-cotyledon >= 1.3.0
Requires:       python-flask >= 0.10.0
Requires:       python-retrying >= 1.2.3

%description -n python2-%{service}
%{common_desc}

This package contains the Kuryr Kubernetes Python library.

%package -n python2-%{service}-tests
Summary:        Kuryr Kubernetes tests

BuildRequires:  python2-oslotest
BuildRequires:  python2-testtools

Requires:       python2-%{service} = %{version}-%{release}
Requires:       python2-mock >= 2.0
Requires:       python2-oslotest >= 1.10.0
Requires:       python2-testrepository >= 0.0.18
Requires:       python2-testscenarios >= 0.4
Requires:       python2-ddt >= 1.0.1
Requires:       python2-testtools >= 1.4.0

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

BuildRequires: python2-sphinx
BuildRequires: python2-reno
BuildRequires: python2-openstackdocstheme

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
%py2_build
PYTHONPATH=. oslo-config-generator --config-file=etc/oslo-config-generator/kuryr.conf
# generate html docs
sphinx-build -W -b html
# generate man pages
sphinx-build -W -b man

%install
%py2_install

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
install -p -D -m 644 %{SOURCE4} %{buildroot}%{_unitdir}/kuryr-cni.service

# Kuryr run directories
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_tmpfilesdir}/openstack-kuryr.conf
install -d %{buildroot}%{_localstatedir}/run/kuryr

# Kuryr cni_ds_init
install -d -m 755 %{buildroot}%{_libexecdir}/%{project}
install -p -D -m 755 cni_ds_init %{buildroot}%{_libexecdir}/%{project}/

%check
%{__python2} setup.py test

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

%post cni
%systemd_post kuryr-cni.service

%preun cni
%systemd_preun kuryr-cni.service

%postun cni
%systemd_postun_with_restart kuryr-cni.service

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
%{_bindir}/kuryr-daemon
%{_unitdir}/kuryr-cni.service
%dir %attr(0755, root, root) %{_libexecdir}/%{project}
%{_libexecdir}/%{project}/cni_ds_init

%changelog
