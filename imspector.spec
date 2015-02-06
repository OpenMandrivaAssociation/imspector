Name:	    imspector
Version:    0.9
Release:    26
Summary:    Multiple IM transparent proxy
License:    GPLv2+
Group:      Networking/Other
URL:        http://www.imspector.org/
Source0:     http://www.imspector.org/downloads/%{name}-20101229.tar.gz
Source1:     imspector.sysconfig
Source2:     imspector.service
Patch0:      imspector-make.patch
Patch1:	     imspector-main.patch
Patch2:	     imspector-conf.patch
Patch3:      multiple-lines.patch
Patch4:      imspector-0.9-openssl-1.0.patch
Patch5:      imspector-0.9-link.patch
BuildRequires:  openssl-devel >= 0.9.7
BuildRequires: mysql-devel
BuildRequires:  postgresql-devel
BuildRequires: sqlite3-devel
Requires:	webserver
Requires:	openssl
Requires:	apache-mod_socache_shmcb # actually, only if webserver is apache, but there is no syntax for such aa condition
Requires(post):   rpm-helper


%description
IMSpector is an Instant Messenger proxy with monitoring, blocking and
content-filtering capabilities. Currently it supports MSN, Jabber/XMPP, AIM,
ICQ, Yahoo, IRC and Gadu-Gadu to different degrees. MSN is the principle
protocol, as it is the most popular these days, at least in the UK where I'm
based. The supported platforms are at present Linux and BSD when using the pf
firewall, but porting to other UNIXs should be trivial. It is able to log to
plain files, as well as several types of SQL database including MySQL, SQLite
and PostreSQL.

%package	mysql
Summary:	Imspector MySQL log support
Group:		Networking/Other
Requires:	%{name}

%description	mysql
This package gives imspector mysql logging capabilities.

%package	postgresql
Summary:	Imspector PostgreSQL log support
Group:		Networking/Other
Requires:	%{name}

%description	postgresql
This package gives imspector postgresql logging capabilities.

%package	sqlite
Summary:	Imspector MySQL log support
Group:		Networking/Other
Requires:	%{name}

%description	sqlite
This package gives imspector sqlite logging and auto-messeging capabilities.

%prep

%setup -q -n imspector
%patch0 -p0 -b .make
%patch1 -p0 -b .notusr
%patch2 -p0 -b .config
%patch3 -p1 -b .multiple_lines_at_config
%patch4 -p0 -b .ssl
%patch5 -p0 -b .link

cat imspector.conf|sed -r 's|/usr/lib|%{_libdir}|' >  imspector.conf.1
rm -f imspector.conf
mv imspector.conf.1 imspector.conf

%build
%make CXX="g++ %{optflags} %ldflags" LIBS="-lcrypto -ldl"
%make mysqlloggingplugin.so CXX="g++ %{optflags}"
%make postgresqlloggingplugin.so CXX="g++ %{optflags}"
%make sqliteloggingplugin.so  CXX="g++ %{optflags}"
%make dbresponderplugin.so CXX="g++ %{optflags}"

%install

%makeinstall
install -d %{buildroot}%{_var}/www/cgi-bin
mv contrib/imspector.cgi %{buildroot}%{_var}/www/cgi-bin/

%{__mkdir_p}  %{buildroot}%{_var}/log/imspector
%{__mkdir_p}  %{buildroot}%{_var}/lib/imspector

# provide a simple apache config
%{__mkdir_p} %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/
cat > %{buildroot}/etc/httpd/conf/webapps.d/imspector.conf << EOF
<Location /cgi-bin/imspector.cgi>
    Require all granted
</Location>
EOF

%{__mkdir_p} %{buildroot}%{_unitdir}
%{__mkdir_p} %{buildroot}%{_sysconfdir}/sysconfig
install -m0755 %{SOURCE2} %{buildroot}%{_unitdir}/imspector.service
install -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/imspector


%preun
%systemd_preun %{name}.service

%pre
%_pre_useradd imspector %{_var}/lib/imspector /bin/false

%postun
%_postun_userdel imspector
%_postun_groupdel imspector
%systemd_postun_with_restart %{name}.service

%post
%_create_ssl_certificate imspector
%systemd_post %{name}.service

%files
%defattr(0755,root,root)
%doc COPYING INSTALL README
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/imspector
%attr(0755,root,root) %{_unitdir}/imspector*
%dir %{_sysconfdir}/imspector
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/imspector/acl.txt
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/imspector/badwords.txt
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/imspector/imspector.conf
%{_sbindir}/imspector
%dir %{_libdir}/imspector
%{_libdir}/imspector/aclfilterplugin.so
%{_libdir}/imspector/badwordsfilterplugin.so
%{_libdir}/imspector/catsloggingplugin.so
%{_libdir}/imspector/censordfilterplugin.so
%{_libdir}/imspector/debugloggingplugin.so
%{_libdir}/imspector/fileloggingplugin.so
%{_libdir}/imspector/ggprotocolplugin.so
%{_libdir}/imspector/httpsprotocolplugin.so
%{_libdir}/imspector/icqprotocolplugin.so
%{_libdir}/imspector/ircprotocolplugin.so
%{_libdir}/imspector/jabberprotocolplugin.so
%{_libdir}/imspector/miscfilterplugin.so
%{_libdir}/imspector/msnprotocolplugin.so
%{_libdir}/imspector/yahooprotocolplugin.so
%{_libdir}/libimspector.so
%{_var}/www/cgi-bin/imspector.cgi
%attr(-,imspector,imspector) %{_var}/lib/imspector
%attr(-,imspector,imspector) %{_var}/log/imspector
%config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/imspector.conf

%files mysql
%{_libdir}/imspector/mysqlloggingplugin.so

%files postgresql
%{_libdir}/imspector/postgresqlloggingplugin.so

%files sqlite
%{_libdir}/imspector/sqliteloggingplugin.so
%{_libdir}/imspector/dbresponderplugin.so




