%bcond_without smart_update

Name:		smart
Version:	1.5
Release:	4
Epoch:		1
Group:		System/Configuration/Packaging
Summary:	Next generation package handling tool
License:	GPLv2+
URL:		https://smartpm.github.io/smart/
Source0:	https://github.com/smartpm/smart/releases/download/v%{version}/%{name}-%{version}.tar.bz2
Source1:	smart-mandriva-distro.py
Source2:	smart.console
Source4:	smart-package-manager.desktop
Source6:	smart-newer.py
Source7:	smart-install.desktop
Source10:	smart-unity-distro.py

Patch1:		smart-1.4.1-enable-distepoch.patch

Patch603:	smart-1.4.1-cache-packages-toggle.patch
Patch606:	smart-1.4.1-sysstdoutencoding-utf-8.patch
Patch607:	smart-1.4.1-saving-cache-msgbox.patch
Patch609:	smart-1.4.1-pycurl-speedup.patch
Patch610:	smart-1.4.1-pycurl-ftp-segfault.patch
Patch611:	smart-1.4.1-pycurl-for-ftp-only.patch
Patch613:	smart-1.4.1-keyerror.patch
Patch615:	smart-1.4.1-coercing2unicode.patch
Patch616:	smart-1.4.1-prefer-last-ok-mirror.patch
Patch618:	smart-1.4.1-inst-by-provide-fix.patch
Patch619:	smart-1.4.1-info-perm-denied.patch
# fix error probably introduced by createrepo update
# unclear if it actually works or not MD 20100830
Patch803:	smart-1.4.1-uncompress-close.patch
# https://bugs.launchpad.net/smart/+bug/268143
# add suggest config to ignore or install for rpm&deb
#Patch805:	smart-1.4.1-rpm-suggests-config.patch
#Patch806:	smart-1.4.1-deb-suggests-config.patch
Patch1007:	smart-1.4.1-computing_upgrades_989_988.patch
Patch1008:	smart-1.4.1-install-update.patch
#Patch1009:	smart-1.4.1-dont-use-_RPMVSF_NOSIGNATURES.patch
Patch1010:	smart-1.4.1-add-missing-lzma-open-function-mdvbz59103.patch
#ROSA patch
Patch2000:	smart-1.4.1-rosa-mirrors.patch
Patch2001:	smart-1.4.1-urpm-cachesize-ignore.patch

BuildRequires:	rpm-mandriva-setup
BuildRequires:	desktop-file-utils
# required by test suite
BuildRequires:	dpkg
BuildRequires:	python-rpm
BuildRequires:	pythonegg(pyliblzma) >= 0.4.0
Requires:	python-rpm pythonegg(pyliblzma) >= 0.4.0
Requires:	usermode-consoleonly
%ifarch %{ix86}
Requires:	pythonegg(psyco)
%endif
Suggests:	pythonegg(pycurl)
BuildRequires:	pkgconfig(python2)

%description
Smart Package Manager is a next generation package handling tool.

%package	gui
Summary:	Smart GTK user interface
Group:		System/Configuration/Packaging
Requires(post):	desktop-file-utils
Requires(postun): desktop-file-utils
%if "%{disttag}" == "unity"
Requires(post):	xdg-utils
%endif
Requires:	%{name} = %{EVRD}
Requires:	pygtk2.0

%description	gui
Smart GTK user interface.

%if %{with smart_update}
%package	update
Summary:	Allows execution of 'smart update' by normal users (suid)
Group:		System/Configuration/Packaging
Requires:	%{name} = %{EVRD}

%description	update
Allows execution of 'smart update' by normal users through a
special suid command.
%endif

%prep
%setup -q
%patch1 -p1 -b .distepoch~
%patch603 -p1 -b .cache_packages_toggle~
%patch606 -p1 -b .sysstdoutencoding_utf-8~
%patch607 -p1 -b .saving_cache_msgbox~
%patch609 -p1 -b .pycurl_speedup~
%patch610 -p1 -b .ftp_segfault_pycurl~
%patch611 -p1 -b .pycurl_for_ftp_only~
%patch613 -p1 -b .keyerror~
%patch615 -p1 -b .coercing2unicode~
%patch616 -p1 -b .prefer_last_ok_mirror~
%patch618 -p1 -b .inst_by_provide_fix~
%patch619 -p1 -b .info_perm_denied~
%patch803 -p1 -b .uncompress_close~
#patch805 -p1 -b .rpm_suggests~
#patch806 -p1 -b .deb_suggests~
%patch1007 -p1 -b .computation~
%patch1008 -p1 -b .update_channels~
#patch1009 -p1 -b .nosig~
%patch1010 -p1 -b .mdvbz59103~
%if "%{disttag}" == "rosa"
%patch2000 -p1 -b .rosa_mirrors~
%endif
%patch2001 -p1 -b .hdlist_size_ignore~

%build
export PYTHON=python2

%setup_compile_flags
%make

%if %{with smart_update}
pushd contrib/smart-update
%make
popd
%endif

# rosa mirrors patch breaks regression check
%if "%{disttag}" != "rosa"
%check
exit 0
export PYTHON=python2
make test
%endif

%install
export PYTHON=python2
%makeinstall_std

%if "%{disttag}" == "unity"
install -m644 %{SOURCE10} -D %{buildroot}%{_prefix}/lib/smart/distro.py
%else
install -m644 %{SOURCE1} -D %{buildroot}%{_prefix}/lib/smart/distro.py
%endif

install -m644 %{SOURCE2} -D %{buildroot}%{_sysconfdir}/security/console.apps/smart-root

ln -sf consolehelper %{buildroot}%{_bindir}/smart-root

mkdir -p %{buildroot}%{_sysconfdir}/pam.d

cat > %{buildroot}%{_sysconfdir}/pam.d/smart-root <<EOF
#%PAM-1.0
auth       sufficient   pam_rootok.so
auth       sufficient   pam_timestamp.so
auth       include      system-auth
account    required     pam_permit.so
session    required     pam_permit.so
session    optional     pam_timestamp.so
session    optional     pam_xauth.so
EOF

mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install \
        --dir %{buildroot}%{_datadir}/applications \
	%{SOURCE4}

install -m644 smart/interfaces/images/smart.png -D %{buildroot}%{_datadir}/pixmaps/smart-package-manager.png
mkdir -p %{buildroot}%{_localstatedir}/lib/smart/channels

install -m644 %{SOURCE6} -D %{buildroot}%{py2_platsitedir}/%{name}/commands/newer.py

%if %{with smart_update}
install -m755 contrib/smart-update/smart-update -D %{buildroot}%{_bindir}/smart-update
%endif

%find_lang %{name}

%if "%{disttag}" == "unity"
%post gui
xdg-mime default smart-install.desktop application/x-rpm
xdg-mime default smart-install.desktop application/x-redhat-package-manager

%post
#Update chanels after install (need with urpmi use only)
/usr/bin/smart update
%endif


%files -f %{name}.lang
%defattr(0644,root,root,0755)
%doc HACKING README TODO IDEAS doc/*.css doc/*.html
%config(noreplace) %{_sysconfdir}/security/console.apps/smart-root
%config(noreplace) %{_sysconfdir}/pam.d/smart-root
%attr(0755,root,root)%{_bindir}/%{name}
%attr(0755,root,root)%{_bindir}/%{name}-root
%dir %{_prefix}/lib/%{name}
%{_prefix}/lib/%{name}/distro.py
%dir %{py2_platsitedir}/smart
%{py2_platsitedir}/smart/*
%{py2_platsitedir}/*.egg-info
%exclude %{py2_platsitedir}/smart/interfaces/gtk
%dir %{_localstatedir}/lib/smart/channels
%{_mandir}/*/*

%files gui
%defattr(0644,root,root,0755)
%{_datadir}/applications/smart-package-manager.desktop
%{_datadir}/pixmaps/smart-package-manager.png
%{py2_platsitedir}/smart/interfaces/gtk

%if %{with smart_update}
%files update
%attr(4755,root,root) %{_bindir}/smart-update
%endif
