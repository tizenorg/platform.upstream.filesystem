%define disable_docs_package 1
%define debug_package %{nil}
Name:           filesystem
Version:        3.1
Release:        0
License:        Public Domain
Summary:        The basic directory layout for a Linux system
Url:            https://fedorahosted.org/filesystem
Group:          Base/Configuration
BuildRequires:  pkgconfig(libtzplatform-config)
Requires(pre): setup
Source2:        languages
Source3:        languages.man


%description
The filesystem package is one of the basic packages that is installed
on a Linux system. Filesystem contains the basic directory layout
for a Linux operating system, including the correct permissions for
the directories.

%prep
rm -f $RPM_BUILD_DIR/filelist

%build

%install
function create_dir () {
    local MODE=$1
    case "$MODE" in
     \#*) return ;;
    esac
    local OWNR=$2
    local GRUP=$3
    local NAME=$4
    local XTRA=$5
    local BDIR=`dirname $NAME`
    test -d "$RPM_BUILD_ROOT/$NAME" && { echo "dir $NAME does already exist" ; echo "input out of sequence ?" ; exit 1 ; }
    test -n "$BDIR" -a ! -d $RPM_BUILD_ROOT$BDIR && create_dir 0755 root root $BDIR
    mkdir -m $MODE $RPM_BUILD_ROOT/$NAME
    echo "$XTRA%%dir %%attr($MODE,$OWNR,$GRUP) $NAME" >> $RPM_BUILD_DIR/filelist
}

cd %{buildroot}

mkdir -p boot dev \
        etc/{X11/{applnk,fontpath.d},xdg/autostart,ld.so.conf.d,opt,pm/{config.d,power.d,sleep.d},xinetd.d,skel,sysconfig,pki} \
        home media mnt %{buildroot}%{TZ_SYS_HOME}/app \
	%{buildroot}%{TZ_SYS_HOME}/developer proc root run/lock srv sys tmp \
        usr/{bin,etc,games,include,%{_lib}/{pkgconfig,games,sse2,tls,X11,pm-utils/{module.d,power.d,sleep.d}},lib/{games,locale,modules,sse2},libexec,local/{bin,etc,games,lib,%{_lib},sbin,src,share/{applications,man/man{1,2,3,4,5,6,7,8,9,n,1x,2x,3x,4x,5x,6x,7x,8x,9x},info},libexec,include,},sbin,share/{help/C,aclocal,applications,augeas/lenses,backgrounds,desktop-directories,dict,doc,empty,games,ghostscript/conf.d,gnome,icons,idl,info,man/man{1,2,3,4,5,6,7,8,9,n,1x,2x,3x,4x,5x,6x,7x,8x,9x,0p,1p,3p},mime-info,misc,omf,pixmaps,sounds,themes,xsessions,X11},src,src/kernels,src/debug} \
        var/{adm,empty,gopher,lib/{empty,games,misc,rpm-state},local,lock/subsys,log,nis,preserve,run,spool/{mail,lpd,uucp},tmp,db,cache,opt,games,yp} \
	%{buildroot}%{TZ_SYS_DB} \
	opt/usr/dbspace \
        opt/usr/{media,share} \
        usr/apps

ln -snf ../var/tmp usr/tmp
ln -snf spool/mail var/mail
ln -snf usr/bin bin
ln -snf usr/sbin sbin
ln -snf usr/lib lib
ln -snf usr/%{_lib} %{_lib}

# Create the locale directories:
while read LANG ; do
  echo "%lang(${LANG}) %ghost %config(missingok) /usr/share/locale/${LANG}" >>$RPM_BUILD_DIR/filelist
  create_dir 0755 root root /usr/share/locale/$LANG/LC_MESSAGES
  create_dir 0755 root root /usr/share/help/$LANG
done < %{SOURCE2}
# Create the locale directories for man:
while read LANG ; do
  create_dir 0755 root root /usr/share/man/$LANG
  for sec in 1 2 3 4 5 6 7 8 9 n; do
    create_dir 0755 root root /usr/share/man/$LANG/man$sec 
##"%lang(${LANG}) %ghost %config(missingok)"
  done
done < %{SOURCE3}


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
posix.symlink("%{TZ_SYS_HOME}/app", "%{TZ_SYS_HOME}/app")
posix.symlink("%{TZ_SYS_HOME}/developer", "%{TZ_SYS_HOME}/developer")

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
%attr(700,app,app) %{TZ_SYS_HOME}/app
%attr(700,developer,developer) %{TZ_SYS_HOME}/developer
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
%dir %attr(755,root,root) %{TZ_SYS_DB}
%dir %attr(755,root,root) /opt/usr
%dir %attr(755,root,app) /opt/usr/dbspace
%dir %attr(755,app,app) /opt/usr/media
%dir %attr(755,app,app) /opt/usr/share
%attr(555,root,root) /proc
%attr(550,root,root) /root
/run
/sbin
/srv
/sys
%attr(1777,root,root) /tmp
%dir /usr
%attr(755,root,root) /usr/apps
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
/usr/share/help/C
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
