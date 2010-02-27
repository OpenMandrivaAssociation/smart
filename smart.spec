%if %mdkversion <= 200910
%bcond_without ksmarttray
%else
%bcond_with    ksmarttray
%endif
%bcond_without smart_update

Name:		smart
Version:	1.3
Release:	%mkrel 1
Epoch:		1
Group:		System/Configuration/Packaging
Summary:	Next generation package handling tool
License:	GPLv2+
URL:		http://smartpm.org
#(peroyvind): This isn't really the upstream version, but rather made out of my
# own Mandriva branch at https://code.launchpad.net/~proyvind/smart/mandriva
# containing all the mandriva patches merged, various bug fixes and new mandriva
# specific features such as the urpmichannelsync plugin.
# Please do *NOT* update smart with upstream version until my branch has been
# fully merged, doing so will break a lot of stuff and also reintroduce bugs
# already fixed, not to mention running the risk of being both pushed and
# shoved at the same time up and down the stairs repeatedly untill you've
# discovered the terrible secret of space and then some! For any questions
# about this branch, just ask! :)
Source0:	http://labix.org/download/smart/%{name}-%{version}.tar.xz
Source1:	smart-mandriva-distro.py
Source2:	smart.console
Source4:	smart-package-manager.desktop
Source6:	smart-newer.py

BuildRequires:	rpm-mandriva-setup
BuildRequires:	desktop-file-utils
# required by test suite
BuildRequires:	dpkg
BuildRequires:	python-rpm
BuildConflicts:	python-curl
Requires:	python-rpm python-liblzma >= 0.4.0
Requires:	usermode-consoleonly
%ifarch %{ix86}
Requires:	python-psyco
%endif
Suggests:	python-curl
%py_requires -d
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Smart Package Manager is a next generation package handling tool.

%package	gui
Summary:	Smart GTK user interface
Group:		System/Configuration/Packaging
Requires(post):	desktop-file-utils
Requires(postun): desktop-file-utils
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	pygtk2.0

%description	gui
Smart GTK user interface.

%if %{with smart_update}
%package	update
Summary:	Allows execution of 'smart update' by normal users (suid)
Group:		System/Configuration/Packaging
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description	update
Allows execution of 'smart update' by normal users through a
special suid command.
%endif

%if %{with ksmarttray}
%package -n	ksmarttray
Summary:	KDE tray program for watching updates with Smart Package Manager
Group:		System/Configuration/Packaging
Requires(post):	desktop-file-utils
Requires(postun): desktop-file-utils
Requires:	%{name}-update = %{epoch}:%{version}-%{release}
BuildRequires:	kdelibs-devel
BuildRequires:	popt
BuildRequires:	rpm-devel
 
%description -n ksmarttray
KDE tray program for watching updates with Smart Package Manager.
%endif

%prep
%setup -q

%build
%setup_compile_flags
%make

%if %{with ksmarttray}
pushd contrib/ksmarttray
make -f admin/Makefile.common

%configure_kde3
%make
popd
%endif

%if %{with smart_update}
pushd contrib/smart-update
%make
popd
%endif

%check
make test

%install
rm -fr %{buildroot}
%makeinstall_std

install -m644 %{SOURCE1} -D %{buildroot}%{_prefix}/lib/smart/distro.py

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

install -m644 %{SOURCE6} -D %{buildroot}%{py_platsitedir}/%{name}/commands/newer.py

%if %{with smart_update}
install -m755 contrib/smart-update/smart-update -D %{buildroot}%{_bindir}/smart-update
%endif

%if %{with ksmarttray}
pushd contrib/ksmarttray
%makeinstall_std
popd

install -m755 contrib/servicemenus/kde_add_smart_channel.sh -D %{buildroot}%{_kde3_bindir}/kde_add_smart_channel.sh
mkdir -p %{buildroot}%{_kde3_datadir}/apps/konqueror/servicemenus
desktop-file-install \
        --dir %{buildroot}%{_kde3_datadir}/apps/konqueror/servicemenus \
        contrib/servicemenus/add_smart_channel.desktop

# XDG menu entry
mkdir -p %{buildroot}%{_kde3_datadir}/applications/
cat > ksmarttray.desktop << EOF
[Desktop Entry]
Name=KSmartTray
Comment=KDE Tray widget for updating RPM files
Exec=%{_kde3_bindir}/ksmarttray %%F
Icon=smart-package-manager
Type=Application
Categories=Qt;KDE;Settings;PackageManager;
EOF

%{_bindir}/desktop-file-install \
        --dir %{buildroot}%{_kde3_datadir}/applications  \
        ksmarttray.desktop
%endif

%find_lang %{name}

%if %mdkversion < 200900
%post gui
%{update_menus}
%{update_desktop_database}
%endif

%if %mdkversion < 200900
%postun gui
%{clean_menus}
%{clean_desktop_database}
%endif

%if %{with ksmarttray}
%if %mdkversion < 200900
%post -n ksmarttray
%{update_menus}
%{update_desktop_database}
%endif

%if %mdkversion < 200900
%postun -n ksmarttray
%{clean_menus}
%{clean_desktop_database}
%endif
%endif

%clean
rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(0644,root,root,0755)
%doc HACKING README TODO IDEAS doc/*.css doc/*.html
%config(noreplace) %{_sysconfdir}/security/console.apps/smart-root
%config(noreplace) %{_sysconfdir}/pam.d/smart-root
%attr(0755,root,root)%{_bindir}/%{name}
%attr(0755,root,root)%{_bindir}/%{name}-root
%dir %{_prefix}/lib/%{name}
%{_prefix}/lib/%{name}/distro.py
%dir %{py_platsitedir}/smart
%{py_platsitedir}/smart/*
%{py_platsitedir}/*.egg-info
%exclude %{py_platsitedir}/smart/interfaces/gtk
%dir %{_localstatedir}/lib/smart/channels
%{_mandir}/*/*

%files gui
%defattr(0644,root,root,0755)
%{_datadir}/applications/smart-package-manager.desktop
%{_datadir}/pixmaps/smart-package-manager.png
%{py_platsitedir}/smart/interfaces/gtk

%if %{with smart_update}
%files update
%attr(4755,root,root) %{_bindir}/smart-update
%endif

%if %{with ksmarttray}
%files -n ksmarttray
%defattr(-,root,root)
%{_kde3_bindir}/ksmarttray
%{_kde3_bindir}/kde_add_smart_channel.sh
%{_kde3_datadir}/apps/ksmarttray
%{_kde3_datadir}/applications/ksmarttray.desktop
%{_kde3_datadir}/apps/konqueror/servicemenus/add_smart_channel.desktop
%{_kde3_iconsdir}/hicolor/48x48/apps/ksmarttray.png
%endif
