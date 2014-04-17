%bcond_without smart_update

Name:		smart
Version:	1.4.1
Release:	13
Epoch:		1
Group:		System/Configuration/Packaging
Summary:	Next generation package handling tool
License:	GPLv2+
URL:		https://code.launchpad.net/smart
Source0:	https://launchpad.net/smart/trunk/%{version}/+download/%{name}-%{version}.tar.bz2
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
Patch805:	smart-1.4.1-rpm-suggests-config.patch
Patch806:	smart-1.4.1-deb-suggests-config.patch
Patch1007:	smart-1.4.1-computing_upgrades_989_988.patch
Patch1008:	smart-1.4.1-install-update.patch
Patch1009:	smart-1.4.1-dont-use-_RPMVSF_NOSIGNATURES.patch
Patch1010:	smart-1.4.1-add-missing-lzma-open-function-mdvbz59103.patch
#ROSA patch
Patch2000:	smart-1.4.1-rosa-mirrors.patch
Patch2001:	smart-1.4.1-urpm-cachesize-ignore.patch

BuildRequires:	rpm-mandriva-setup
BuildRequires:	desktop-file-utils
# required by test suite
BuildRequires:	dpkg
BuildRequires:	python-rpm
Requires:	python-rpm pythonegg(pyliblzma) >= 0.4.0
Requires:	usermode-consoleonly
%ifarch %{ix86}
Requires:	pythonegg(psyco)
%endif
Suggests:	pythonegg(pycurl)
BuildRequires:	pkgconfig(python)

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
%patch805 -p1 -b .rpm_suggests~
%patch806 -p1 -b .deb_suggests~
%patch1007 -p1 -b .computation~
%patch1008 -p1 -b .update_channels~
%patch1009 -p1 -b .nosig~
%patch1010 -p1 -b .mdvbz59103~
%if "%{disttag}" == "rosa"
%patch2000 -p1 -b .rosa_mirrors~
%endif
%patch2001 -p1 -b .hdlist_size_ignore~

%build
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
make test
%endif

%install
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

install -m644 %{SOURCE6} -D %{buildroot}%{py_platsitedir}/%{name}/commands/newer.py

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


%changelog
* Fri May 18 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.4.1-3
+ Revision: 799466
- d'oh, patch wasn't finished in previous release..:|
- don't use _RPMVSF_NOSIGNATURES ~constant (fixes breakage with rpm >= 5.4.9)

* Fri Jan 20 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.4.1-1
+ Revision: 763291
- add amois computational speed up patch (P1007, from Unity Linux)
- add --update & --update-channels options for 'smart install' &
--update-channels for 'smart upgrade' (P1008, from Unity Linux)
- make sure to close input & output files after decompression (P803, from Unity
  Linux)
- use pythonegg() dependencies
- fix info command exception when redirecting to file/pipe (P606, from Unity
  Linux)
- set smart-install.desktop to default mimetype for application/x-rpm if built
  for unity linux
- install unity specific distro.py if built on unity
- make behaviour of handlig Suggests configurable (P805 & P806, from Unity Linux)
- add a message box outputting "Saving cache..." in gui when saving cache (P607,
  from Unity Linux)
- fix so that 'smart install foo' will work even if anything providing 'foo' is
  installed (P618, from Unity Linux)
- output warning about configuration being in read-only mode if trying to reload
  channels in read-only mode (P619, from Unity Linux)
- fix update progress stopping when refetching invalid package (#lp:538807)
  and smart update crashing on first run with many channels (#lp:244605) (P613)
- workaround AttributeError thrown in FTPHandler.fetch() (P615, [#lp:535628])
- download single channel metadata from the same mirror [#lp:539601] and to
  support prefer-origin option that makes Smart prefer primary mirrors (P616)
- use pycurl for ftp only (P611, from Unity Linux)
- fix pycurl ftp segfault (P610, [#lp:533805], unitybz#338)
- add back pycurl speedup patch (P609)
- add support for toggling to keep packages in /var/lib/smart/packages after
  install (P603, from Unity Linux)
- add smart applet (from Unity Linux)
- use %%{EVRD} macro
- 1.4.1 (upstream version, mandriva branch has been merged)
- drop legacy rpm stuff..
- enable rpm ordering by default

* Fri Jan 28 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.4-1.r951.1
+ Revision: 633562
- implement distepoch support

* Fri Oct 29 2010 Michael Scherer <misc@mandriva.org> 1:1.4-1.r949.2mdv2011.0
+ Revision: 590080
- rebuild for python 2.7

* Sat Oct 02 2010 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.4-1.r949.1mdv2011.0
+ Revision: 582426
- New release: 1.4 (merging in latest code from trunk)

* Thu Apr 22 2010 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.3.1-0.r948.1mdv2010.1
+ Revision: 537821
- update to revision 948:
  	o fix loading of old cache lacking new channel attribute (fixes #58144)
  	o revert an accidental change that were commited in r942
- remove scriptlets for < 2009.0 releases
- update to revision 946 to fix a build failure and a couple of test failures
- new bzr snapshot:
  	o fixes gtk gui breakage with channel updating
  	o merges latest code from trunk & unity branch

* Sat Feb 27 2010 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.3-1mdv2010.1
+ Revision: 512282
- new release: 1.3 (synced mandriva branch with trunk)
- use %%setup_compile_flags macro

* Sun Sep 27 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.2-10mdv2010.0
+ Revision: 449900
- make multilib behaviour optionable and also apply the behaviour to package
  upgrades as well (updates P501)
- move distro.py to standard location as it no longer contains any arch specific
  stuff...
- fix slow pycurl fetcher without breaking others..
- fix huge slowdown limiting download speed to ~160K/sec when using pycurl
- for a dependency which only two packages of same version and different arch
  satisfies, automatically pick the one with best arch score. This will ie.
  make smart able to automatically pick 'lib64foo-devel' to satisfy 'foo-devel'
  in cases where both 'libfoo-devel' & 'lib64foo-devel' provides it. (P501)
- restore old revision after accidental removal of directory
- fixes and updates from smart mandriva branch (P500):
  	o really fix handling of hdlist.cz to make it actually work again
  	o make sure that mirror picked by urpmisync plugin may actually be used
  	o add XZHandler for handling xz compressed files

* Tue Jun 02 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.2-8mdv2010.0
+ Revision: 382279
- add a buildconflicts on python-curl to prevent it's different output breaking test suite
- update to new tarball generated from my branch:
  	o fix handling of restricted channels (fixes #51249)
  	o fix handling of cdrom (fixes #51247)
  	o fix baseurl so that downloading will work again (fixes #50460)
  	o print warning if errors resulting in urpmisync being disabled occurs

* Mon May 25 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.2-7mdv2010.0
+ Revision: 379714
- disable ksmarttray for >= 2010.0
- * make urpmisync more sturdy, remove channels when disabled and fallback to
  disabled if exceptions occurs (P505)
- fix decompression of hdlist.cz (P504)

* Sat Apr 25 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.2-6mdv2010.0
+ Revision: 369038
- skip global options urpmi.cfg for urpmichannelsync (fixes #48509,8)
- fix dealing with urpmi medias containing dots in the name (P502)

* Tue Mar 10 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.2-5mdv2009.1
+ Revision: 353349
- make urpmichannelsync channels default to 0 for priority to keep consistent
  priority of packages based on their version only which is what one usually wants..
- be sure to move hdlist if present as well updates (P0)

* Mon Mar 09 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.2-4mdv2009.1
+ Revision: 353328
- reuse existing urpmi metadata when forcing migration to new layout and remove
  any old leftovers (P0)

* Sat Mar 07 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.2-3mdv2009.1
+ Revision: 350674
- add python-rpm to buildrequires (required by test suite)
- add %%check section with test suite running to prevent more silly mistakes..:p
- gah, previous commit/release missed the actually updated tarball, update it
  from my branch again with more fixes:
  	o in situations where /var/lib/media/<medianame>/ doesn't exist, create it,
  	  will force urpmi to migrate to new layout from old with
  	  /var/lib/media/synthesis.hdlist.<medianame>.cz etc. as well.
  	o fix broken urpmichannelsync test
  	o fix locale issue which would break the test suite
  	o fix issue where dpkg installed, but not used would break smart

* Fri Mar 06 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.2-2mdv2009.1
+ Revision: 349658
- fix mess with unresolved conflicts which made it in to the branch by accident:(

* Thu Mar 05 2009 Per Øyvind Karlsen <peroyvind@mandriva.org> 1:1.2-1mdv2009.1
+ Revision: 349177
- update to new version based on my branch:
  	o merging in new 1.2 stable release from trunk
  	o merge in several of afb's bugfix and relevant feature branches which hasn't
  	  made their way to trunk yet
  	o improve urpmichannelsync plugin making it a bit more robust
  	o merge all of our appropriate patches and throw away those who's not
  	o switch to xz compression for tarball
  fix up after previous vandalism commit:
  	o revert back to my mandriva branch
  	o fix reckless usage of epoch tag which broke dependencies on subpackages
  	o fix #48265 properly

* Thu Feb 26 2009 Helio Chissini de Castro <helio@mandriva.com> 1:1.1-3mdv2009.1
+ Revision: 345173
- Fixing bug https://qa.mandriva.com/show_bug.cgi?id=48265 with a easy solution, using the real upstream package.
  In near future, we should accept only upstream tarballs, instead of use unfinished obscure branchs

* Thu Dec 25 2008 Funda Wang <fwang@mandriva.org> 1.1.1-2mdv2009.1
+ Revision: 318616
- fix patch
- rediff signature patch
- rediff channel patch
- rebuild for new python

* Wed Nov 05 2008 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.1.1-1mdv2009.1
+ Revision: 300004
- workaround nagging about missing files during build of ksmarttray
- perform some spec cleanups and cosmetics to follow "regular" Mandriva style
- update from my own branch based on 1.1.1:
  	o adds urpimsync plugin to natively supporting use of local urpmi
  	  configuration and data (replaces existing distro.py and obsoletes
  	  urpmi2smart)
  	o adds basic mirrorlist support
- make dependency on python-liblzma versioned

* Mon Sep 15 2008 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.1-1mdv2009.0
+ Revision: 285039
- since last one never got through, bump release down back to 1
- bump release
- cool down on overeager macro usage for %%{name}
- change conflicts on python-curl to suggests
- add dependency on python-liblzma since we need it for info.xml.lzma
- add support for info.xml metadata and fix crash with curl (P200, from my own branch:)
- fix string splitting in urpmi2smart that got broken due to a second ':' showing
  up in new mirrorurl variable
- new release
- remove conflict on python-curl, new version of python-curl works without
  segfaulting :)
- always pass -pX argument to %%patchX

* Fri Aug 15 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 1.0-1mdv2009.0
+ Revision: 272233
- Update to Smart 1.0
  Remove patches 0, 2,6 ,11 ( Merged upstream )
  Added comment about patch 13 ( i do not know if this is still needed to use it )

* Fri Aug 08 2008 Thierry Vignaud <tv@mandriva.org> 0.52-7mdv2009.0
+ Revision: 269254
- rebuild early 2009.0 package (before pixel changes)

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas
    - ensure comment does not appear in ksmarttray's %%postun

* Sat Jun 07 2008 Funda Wang <fwang@mandriva.org> 0.52-6mdv2009.0
+ Revision: 216583
- use media_info and synthesis by default
- move kde3 stuff to /opt

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

* Thu Jan 31 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 0.52-5mdv2008.1
+ Revision: 160889
- fix smart widht when running in terminal, patch 105

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Mon Dec 17 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 0.52-4mdv2008.1
+ Revision: 121130
- use SUSE patches
- drop patches 100-102
- rebuild for new rpm
- new license policy
- do not package LICENSE file

* Mon Oct 22 2007 David Walluck <walluck@mandriva.org> 0.52-3mdv2008.1
+ Revision: 101073
- always include ksmarttray patches in src.rpm
- always apply ksmarttray patches regardless of whether we are building it

* Thu Oct 18 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 0.52-2mdv2008.1
+ Revision: 99836
- drop patch 9 (merged in one SUSE patch)
- add three SUSE patches (x86_64 support)

* Tue Oct 09 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 0.52-1mdv2008.1
+ Revision: 96573
- remove patch 2 as it has been applied upstream
- new version
- *.pyc files should be shipped

* Thu Sep 27 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 0.51-17mdv2008.0
+ Revision: 93301
- do not hardcode libdir
- conflicts python-curl as it crashesh smart while updating channels
- do not ship *.pyc files
-  add full url for source0
- enable ksmarttray (somehow i just disabled it ;)
- use smart's makefile
- fix mixture of tabs and spaces
- do not use vendor in desktop files
- move patch 12 to ksmarttray section
- suggests python-curl

* Sat Sep 15 2007 David Walluck <walluck@mandriva.org> 0.51-16mdv2008.0
+ Revision: 85891
- require smart = %%{version}-%%{release} from subpackages so we don't get breakage

* Sat Sep 15 2007 David Walluck <walluck@mandriva.org> 0.51-15mdv2008.0
+ Revision: 85877
- fix conflicts with gui subpackage

* Fri Sep 14 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 0.51-14mdv2008.0
+ Revision: 85627
- check rpm signatures and add default pgp keyserver
  provide patch 14, which prevents segfaults on slower connections
  provide patch 15, which add support for fail on curl authentification error
  provide patch 16, which add Hide-Unlocked option in View menu
  provide patch 17, which should haven't slowndown on curl downloading
  set requires on python-curl, especially useful for people using proxies

* Thu Sep 13 2007 Thierry Vignaud <tv@mandriva.org> 0.51-13mdv2008.0
+ Revision: 85237
- bump conflicts in order to fix upgrade (#33465)

* Thu Sep 13 2007 David Walluck <walluck@mandriva.org> 0.51-12mdv2008.0
+ Revision: 84932
- bump release
- remove executable bit from smart-package-manager.desktop
- document some outstanding issues

* Thu Sep 13 2007 David Walluck <walluck@mandriva.org> 0.51-10mdv2008.0
+ Revision: 84913
- partial fix for upstream ksmarttray update bug
- fix for bug #28782 (detectsys)

* Sun Sep 09 2007 David Walluck <walluck@mandriva.org> 0.51-9mdv2008.0
+ Revision: 83949
- include modified urpmi2smart.py script
- replace references to i568 with i586 in distro.i586
- always include distro.i586 as a source regardless of arch and update at install time
- use %%bcond_without macros for spec options
- add patch to fix downloading over scp
- use desktop-file-install and make sure .desktop files validate
- show ksmarttray in menus

  + Tomasz Pawel Gajc <tpg@mandriva.org>
    - update channel list
      remove JPackage because it is dead
      add non-free channel
      provide separate channel list for i586 and x86_64

* Mon Sep 03 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 0.51-6mdv2008.0
+ Revision: 78579
- use script fo find translations
- remove options for older mdv release
- drop exclude for some files
- ksmarttray will be shown only in KDE menus

* Wed Aug 29 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 0.51-5mdv2008.0
+ Revision: 74263
- remove doubled/unneeded buildrequires
- do not use  %%{_sourcedir}
- remove %%ifarch, rely on libsuffix for configure script
- small cleans in a spec file
- drop source 5 (smart has french translation already)
- provide patch 8 (fixes gui)
- provide patch 9 (speed up listing packages in channels)
- provide patch 5 (should speed up gui responsiveness)

* Tue Aug 28 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 0.51-4mdv2008.0
+ Revision: 72632
- fix build on x86_64
- provides smart newer, a command which shows packages that have available upgrades
- add ksmarttray's konqueror service menus
- add scriplets
- provide patch 4, which adds handling of rpm gpg signatures
- provide patch 3 (mirrors for channels)
- provide patch 2 (should speed up cache loading)
- provide patch 7 (ksmarttray can start smart-gui now)

* Fri Aug 10 2007 Tomasz Pawel Gajc <tpg@mandriva.org> 0.51-3mdv2008.0
+ Revision: 61015
- provide patch 6 (enable build of ksmarttray)
- drop X-MandrivaLinux from desktop file

* Mon Jun 11 2007 Olivier Thauvin <nanardon@mandriva.org> 0.51-2mdv2008.0
+ Revision: 37984
- rebuild for rpm

* Mon May 21 2007 Andreas Hasenack <andreas@mandriva.com> 0.51-1mdv2008.0
+ Revision: 29383
- updated to version 0.51
- removed patches that were already included

* Wed May 02 2007 Funda Wang <fwang@mandriva.org> 0.50-5mdv2008.0
+ Revision: 20377
- Move translations into main package, because vt under x11 may need
  translations.

