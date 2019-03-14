# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
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

%package -n python%{pyver}-%{service}
Summary:        Kuryr Kubernetes libraries
%{?python_provide:%python_provide python2-%{service}}

# debtcollector is a hidden dependency of oslo-config
BuildRequires:  git
BuildRequires:  python%{pyver}-debtcollector
BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-hacking
BuildRequires:  python%{pyver}-oslo-config
BuildRequires:  python%{pyver}-pbr
BuildRequires:  python%{pyver}-setuptools
BuildRequires:  systemd-units
BuildRequires:  python%{pyver}-mock
BuildRequires:  python%{pyver}-oslotest
BuildRequires:  python%{pyver}-testrepository
BuildRequires:  python%{pyver}-testscenarios
BuildRequires:  python%{pyver}-ddt
BuildRequires:  python%{pyver}-testtools
BuildRequires:  python%{pyver}-oslo-log
BuildRequires:  python%{pyver}-oslo-reports
BuildRequires:  python%{pyver}-kuryr-lib
BuildRequires:  python%{pyver}-os-vif
BuildRequires:  python%{pyver}-cotyledon
BuildRequires:  python%{pyver}-flask
BuildRequires:  python%{pyver}-oslo-cache

# Handle python2 exception
%if %{pyver} == 2
BuildRequires:  python-d2to1
BuildRequires:  python-retrying
%else
BuildRequires:  python%{pyver}-d2to1
BuildRequires:  python%{pyver}-retrying
%endif

Requires:       python%{pyver}-%{project}-lib >= 0.5.0
Requires:       python%{pyver}-pyroute2 >= 0.5.1
Requires:       python%{pyver}-requests >= 2.14.2
Requires:       python%{pyver}-eventlet >= 0.18.2
Requires:       python%{pyver}-oslo-cache >= 1.26.0
Requires:       python%{pyver}-oslo-config >= 2:5.2.0
Requires:       python%{pyver}-oslo-log >= 3.36.0
Requires:       python%{pyver}-oslo-reports >= 1.18.0
Requires:       python%{pyver}-oslo-serialization >= 2.18.0
Requires:       python%{pyver}-oslo-service >= 1.24.0
Requires:       python%{pyver}-oslo-utils >= 3.33.0
Requires:       python%{pyver}-os-vif >= 1.7.0
Requires:       python%{pyver}-prettytable >= 0.7.2
Requires:       python%{pyver}-six >= 1.10.0
Requires:       python%{pyver}-stevedore >= 1.20.0
Requires:       python%{pyver}-cotyledon >= 1.3.0
Requires:       python%{pyver}-flask >= 0.12.3

# Handle python2 exception
%if %{pyver} == 2
Requires:       python-retrying >= 1.2.3
%else
Requires:       python%{pyver}-retrying >= 1.2.3
%endif

%description -n python%{pyver}-%{service}
%{common_desc}

This package contains the Kuryr Kubernetes Python library.

%package -n python%{pyver}-%{service}-tests
Summary:        Kuryr Kubernetes tests

BuildRequires:  python%{pyver}-oslotest
BuildRequires:  python%{pyver}-testtools

Requires:       python%{pyver}-%{service} = %{version}-%{release}
Requires:       python%{pyver}-mock >= 2.0
Requires:       python%{pyver}-oslotest >= 1.10.0
Requires:       python%{pyver}-testrepository >= 0.0.18
Requires:       python%{pyver}-testscenarios >= 0.4
Requires:       python%{pyver}-ddt >= 1.0.1
Requires:       python%{pyver}-testtools >= 1.4.0

%description -n python%{pyver}-%{service}-tests
%{common_desc}

This package contains the Kuryr Kubernetes tests.

%package common
Summary:        Kuryr Kubernetes common files
Group:          Applications/System
Requires:   python%{pyver}-%{service} = %{version}-%{release}

%description common
This package contains Kuryr files common to all services.

%if 0%{?with_doc}
%package doc
Summary:    OpenStack Kuryr-Kubernetes documentation

BuildRequires: python%{pyver}-sphinx
BuildRequires: python%{pyver}-reno
BuildRequires: python%{pyver}-openstackdocstheme

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
%{pyver_build}
PYTHONPATH=. oslo-config-generator-%{pyver} --config-file=etc/oslo-config-generator/kuryr.conf
%if 0%{?with_doc}
# generate html docs
sphinx-build-%{pyver} -W -b html doc/source doc/build/html
# generate man pages
sphinx-build-%{pyver} -W -b man doc/source doc/build/man
%endif

%install
%{pyver_install}

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
%{pyver_bin} setup.py test

%pre -n python%{pyver}-%{service}
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

%files -n python%{pyver}-%{service}-tests
%license LICENSE
%{pyver_sitelib}/%{module}/tests

%files -n python%{pyver}-%{service}
%license LICENSE
%{pyver_sitelib}/%{module}
%{pyver_sitelib}/%{module}-*.egg-info
%exclude %{pyver_sitelib}/%{module}/tests

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
