%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x815AFEC729392386480E076DCC0DFE2D21C023C9
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order
# Exclude sphinx from BRs if docs are disabled
%if ! 0%{?with_doc}
%global excluded_brs %{excluded_brs} sphinx openstackdocstheme
%endif
%global project kuryr
%global service kuryr-kubernetes
%global module kuryr_kubernetes
%global with_doc 1

%global common_desc \
Kuryr Kubernetes provides a Controller that watches the Kubernetes API for \
Object changes and manages Neutron resources to provide the Kubernetes Cluster \
with OpenStack networking.

Name:      openstack-%service
Version:   9.0.0
Release:   1%{?dist}
Summary:   OpenStack networking integration with Kubernetes
License:   Apache-2.0
URL:       http://docs.openstack.org/developer/kuryr-kubernetes/

Source0:   https://tarballs.openstack.org/%{service}/%{service}-%{upstream_version}.tar.gz
#

Source1:   kuryr.logrotate
Source2:   kuryr-controller.service
Source3:   openstack-kuryr.tmpfs
Source4:   kuryr-cni.service
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.openstack.org/%{service}/%{service}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch: noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
BuildRequires:  openstack-macros
%endif

Requires(pre): shadow-utils
%{?systemd_requires}

%description
Kuryr-Kubernetes brings OpenStack networking to Kubernetes clusters

%package -n python3-%{service}
Summary:        Kuryr Kubernetes libraries

BuildRequires:  git-core
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  systemd-units
%description -n python3-%{service}
%{common_desc}

This package contains the Kuryr Kubernetes Python library.

%package -n python3-%{service}-tests
Summary:        Kuryr Kubernetes tests

Requires:       python3-%{service} = %{version}-%{release}
Requires:       python3-mock >= 2.0
Requires:       python3-oslotest >= 1.10.0
Requires:       python3-testrepository >= 0.0.18
Requires:       python3-testscenarios >= 0.4
Requires:       python3-ddt >= 1.0.1
Requires:       python3-testtools >= 1.4.0
Requires:       python3-stestr

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
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{service}-%{upstream_version} -S git

find %{module} -name \*.py -exec sed -i '/\/usr\/bin\/env python/{d;q}' {} +



sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif

%build
%pyproject_wheel
%if 0%{?with_doc}
# generate html docs
%tox -e docs
# generate man pages
sphinx-build -W -b man doc/source doc/build/man
%endif

%install
%pyproject_install
# generate config file
PYTHONPATH=%{buildroot}/%{python3_sitelib} oslo-config-generator --config-file=etc/oslo-config-generator/kuryr.conf
# The automatic value of pybasedir is wrong and unneeded and makes build to fail
sed -i "/#pybasedir.*/d" etc/kuryr.conf.sample

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
export OS_TEST_PATH='./kuryr_kubernetes/tests'
%tox -e %{default_toxenv}

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
%{_bindir}/kuryr-k8s-sanity
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
%{python3_sitelib}/%{module}-*.dist-info
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
* Wed Oct 04 2023 RDO <dev@lists.rdoproject.org> 9.0.0-1
- Update to 9.0.0

* Fri Sep 15 2023 RDO <dev@lists.rdoproject.org> 9.0.0-0.1.0rc1
- Update to 9.0.0.0rc1

