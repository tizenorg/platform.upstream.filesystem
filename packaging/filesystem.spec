%define disable_docs_package 1
%define debug_package %{nil}
Name:           filesystem
Version:        3.1
Release:        2%{?dist}
License:        Public Domain
Summary:        The basic directory layout for a Linux system
Url:            https://fedorahosted.org/filesystem
Group:          System Environment/Base
# Raw source1 URL: https://fedorahosted.org/filesystem/browser/lang-exceptions?format=raw
Source1:        https://fedorahosted.org/filesystem/browser/lang-exceptions
Source2:        iso_639.sed
Source3:        iso_3166.sed
BuildRequires:  iso-codes
Requires(pre): setup


%description
The filesystem package is one of the basic packages that is installed
on a Linux system. Filesystem contains the basic directory layout
for a Linux operating system, including the correct permissions for
the directories.

%prep
rm -f $RPM_BUILD_DIR/filelist

%build

%install
install -p -c -m755 %{SOURCE2} %{buildroot}/iso_639.sed
install -p -c -m755 %{SOURCE3} %{buildroot}/iso_3166.sed

cd %{buildroot}

mkdir -p boot dev \
        etc/{X11/{applnk,fontpath.d},xdg/autostart,opt,pm/{config.d,power.d,sleep.d},xinetd.d,skel,sysconfig,pki} \
        home media mnt opt proc root run/lock srv sys tmp \
        usr/{bin,etc,games,include,%{_lib}/{games,sse2,tls,X11,pm-utils/{module.d,power.d,sleep.d}},lib/{games,locale,modules,sse2},libexec,local/{bin,etc,games,lib,%{_lib},sbin,src,share/{applications,man/man{1,2,3,4,5,6,7,8,9,n,1x,2x,3x,4x,5x,6x,7x,8x,9x},info},libexec,include,},sbin,share/{aclocal,applications,augeas/lenses,backgrounds,desktop-directories,dict,doc,empty,games,ghostscript/conf.d,gnome,icons,idl,info,man/man{1,2,3,4,5,6,7,8,9,n,1x,2x,3x,4x,5x,6x,7x,8x,9x,0p,1p,3p},mime-info,misc,omf,pixmaps,sounds,themes,xsessions,X11},src,src/kernels,src/debug} \
        var/{adm,empty,gopher,lib/{empty,games,misc,rpm-state},local,lock/subsys,log,nis,preserve,run,spool/{mail,lpd,uucp},tmp,db,cache,opt,games,yp}

ln -snf ../var/tmp usr/tmp
ln -snf spool/mail var/mail
ln -snf usr/bin bin
ln -snf usr/sbin sbin
ln -snf usr/lib lib
ln -snf usr/%{_lib} %{_lib}

sed -n -f %{buildroot}/iso_639.sed /usr/share/xml/iso-codes/iso_639.xml \
  >%{buildroot}/iso_639.tab
sed -n -f %{buildroot}/iso_3166.sed /usr/share/xml/iso-codes/iso_3166.xml \
  >%{buildroot}/iso_3166.tab

grep -v "^$" %{buildroot}/iso_639.tab | grep -v "^#" | while read a b c d ; do
    [[ "$d" =~ "^Reserved" ]] && continue
    [[ "$d" =~ "^No linguistic" ]] && continue

    locale=$c
    if [ "$locale" = "XX" ]; then
        locale=$b
    fi
    echo "%lang(${locale})	/usr/share/locale/${locale}" >> $RPM_BUILD_DIR/filelist
    echo "%lang(${locale}) %ghost %config(missingok) /usr/share/man/${locale}" >>$RPM_BUILD_DIR/filelist
done
cat %{SOURCE1} | grep -v "^#" | grep -v "^$" | while read loc ; do
    locale=$loc
    locality=
    special=
    [[ "$locale" =~ "@" ]] && locale=${locale%%%%@*}
    [[ "$locale" =~ "_" ]] && locality=${locale##*_}
    [[ "$locality" =~ "." ]] && locality=${locality%%%%.*}
    [[ "$loc" =~ "_" ]] || [[ "$loc" =~ "@" ]] || special=$loc

    # If the locality is not official, skip it
    if [ -n "$locality" ]; then
        grep -q "^$locality" %{buildroot}/iso_3166.tab || continue
    fi
    # If the locale is not official and not special, skip it
    if [ -z "$special" ]; then
        egrep -q "[[:space:]]${locale%%_*}[[:space:]]" \
           %{buildroot}/iso_639.tab || continue
    fi
    echo "%lang(${locale})	/usr/share/locale/${loc}" >> $RPM_BUILD_DIR/filelist
    echo "%lang(${locale})  %ghost %config(missingok) /usr/share/man/${loc}" >> $RPM_BUILD_DIR/filelist
done

rm -f %{buildroot}/iso_639.tab
rm -f %{buildroot}/iso_639.sed
rm -f %{buildroot}/iso_3166.tab
rm -f %{buildroot}/iso_3166.sed

cat $RPM_BUILD_DIR/filelist | grep "locale" | while read a b ; do
    mkdir -p -m 755 %{buildroot}/$b/LC_MESSAGES
done

cat $RPM_BUILD_DIR/filelist | grep "/share/man" | while read a b c d; do
    mkdir -p -m 755 %{buildroot}/$d/man{1,2,3,4,5,6,7,8,9,n,1x,2x,3x,4x,5x,6x,7x,8x,9x,0p,1p,3p}
done

for i in man{1,2,3,4,5,6,7,8,9,n,1x,2x,3x,4x,5x,6x,7x,8x,9x,0p,1p,3p}; do
   echo "/usr/share/man/$i" >>$RPM_BUILD_DIR/filelist
done

%pretrans -p <lua>
--#
--# If we are running in pretrans in a fresh root, there is no /usr and symlinks.
--# We cannot be sure, to be the very first rpm in the transaction list,
--# so, let's create the toplevel symlinks here and the directories they point to.
--# When our rpm is unpacked by cpio, it will set all permissions and modes later.
--#

if posix.stat("/usr") == nil then
    posix.mkdir("/usr")
end

for i,dir in ipairs({"/lib", "/%{_lib}", "/sbin", "/bin"}) do
    if posix.stat("/usr"..dir) == nil then
        posix.mkdir("/usr"..dir)
        if posix.stat(dir, "mode") == nil then
            posix.symlink("usr"..dir, dir)
        end
    end
end

return 0

%post -p <lua>
posix.symlink("../run", "/var/run")
posix.symlink("../run/lock", "/var/lock")

%files -f filelist
%defattr(0755,root,root,-)
%dir %attr(555,root,root)
/bin
%attr(555,root,root) /boot
/dev
%dir /etc
%{_sysconfdir}/X11
%{_sysconfdir}/xdg
%{_sysconfdir}/opt
%{_sysconfdir}/pm
%{_sysconfdir}/xinetd.d
%{_sysconfdir}/skel
%{_sysconfdir}/sysconfig
%{_sysconfdir}/pki
/home
/lib
#%ifarch x86_64 ppc ppc64 sparc sparc64 s390 s390x
/%{_lib}
#%endif
/media
%dir /mnt
%dir /opt
%attr(555,root,root) /proc
%attr(550,root,root) /root
/run
/sbin
/srv
/sys
%attr(1777,root,root) /tmp
%dir /usr
%attr(555,root,root) /usr/bin
/usr/etc
/usr/games
/usr/include
%attr(555,root,root) /usr/lib
#%ifarch x86_64 ppc ppc64 sparc sparc64 s390 s390x
%attr(555,root,root) /usr/%{_lib}
#%endif
/usr/libexec
/usr/local
%attr(555,root,root) /usr/sbin
%dir /usr/share
/usr/share/aclocal
/usr/share/applications
/usr/share/augeas
/usr/share/backgrounds
/usr/share/desktop-directories
/usr/share/dict
/usr/share/doc
%attr(555,root,root) %dir /usr/share/empty
/usr/share/games
/usr/share/ghostscript
/usr/share/gnome
/usr/share/icons
/usr/share/idl
/usr/share/info
%dir /usr/share/locale
%dir /usr/share/man
/usr/share/mime-info
/usr/share/misc
/usr/share/omf
/usr/share/pixmaps
/usr/share/sounds
/usr/share/themes
/usr/share/xsessions
/usr/share/X11
/usr/src
/usr/tmp
%dir /var
%{_localstatedir}/adm
%{_localstatedir}/cache
%{_localstatedir}/db
%{_localstatedir}/empty
%{_localstatedir}/games
%{_localstatedir}/gopher
%{_localstatedir}/lib
%{_localstatedir}/local
%ghost %dir %attr(755,root,root) %{_localstatedir}/lock
%ghost %{_localstatedir}/lock/subsys
%{_localstatedir}/log
%{_localstatedir}/mail
%{_localstatedir}/nis
%{_localstatedir}/opt
%{_localstatedir}/preserve
%ghost %attr(755,root,root) %{_localstatedir}/run
%dir %{_localstatedir}/spool
%attr(755,root,root) %{_localstatedir}/spool/lpd
%attr(775,root,mail) %{_localstatedir}/spool/mail
%attr(755,uucp,uucp) %{_localstatedir}/spool/uucp
%attr(1777,root,root) %{_localstatedir}/tmp
%{_localstatedir}/yp

%changelog
