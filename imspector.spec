Name:	    imspector
Version:    0.9
Release:    21
Summary:    Multiple IM transparent proxy
License:    GPLv2+
Group:      Networking/Other
URL:        http://www.imspector.org/
Source0:     http://www.imspector.org/downloads/%{name}-20101229.tar.gz
Source1:     imspector.sysconfig
Source2:     imspector.init
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
%make CXX="g++ %optflags %ldflags" LIBS="-lcrypto -ldl"
%make mysqlloggingplugin.so CXX="g++ %optflags"
%make postgresqlloggingplugin.so CXX="g++ %optflags"
%make sqliteloggingplugin.so  CXX="g++ %optflags"
%make dbresponderplugin.so CXX="g++ %optflags"

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

%{__mkdir_p} %{buildroot}%{_initrddir}
%{__mkdir_p} %{buildroot}%{_sysconfdir}/sysconfig
install -m0755 %{SOURCE2} %{buildroot}%{_initrddir}/imspector
install -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/imspector


%preun
%_preun_service imspector

%pre
%_pre_useradd imspector %{_var}/lib/imspector /bin/false

%postun
%_postun_userdel imspector
%_postun_groupdel imspector

%post
%_create_ssl_certificate imspector
%_post_service imspector

%files
%defattr(0755,root,root)
%doc COPYING INSTALL README
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/imspector
%attr(0755,root,root) %{_initrddir}/imspector
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




%changelog
* Wed Aug 03 2011 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 0.9-20mdv2012.0
+ Revision: 693079
- trying to make this SPEC compatible with mageia so it will be easier for me

* Thu Mar 17 2011 Oden Eriksson <oeriksson@mandriva.com> 0.9-19
+ Revision: 645804
- relink against libmysqlclient.so.18

* Sat Jan 01 2011 Oden Eriksson <oeriksson@mandriva.com> 0.9-18mdv2011.0
+ Revision: 627249
- rebuilt against mysql-5.5.8 libs, again

* Thu Dec 30 2010 Oden Eriksson <oeriksson@mandriva.com> 0.9-17mdv2011.0
+ Revision: 626529
- rebuilt against mysql-5.5.8 libs

* Wed Dec 29 2010 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 0.9-15mdv2011.0
+ Revision: 625827
- Fixes for new MSN protocol from upstream

* Mon Nov 01 2010 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 0.9-14mdv2011.0
+ Revision: 591322
- MSNP21 support
  P1 rediffed

* Fri Jul 16 2010 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 0.9-13mdv2011.0
+ Revision: 554432
- Backport 2008.1-  support

* Fri May 14 2010 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 0.9-12mdv2010.1
+ Revision: 544734
- Conf file was zero, sed error
- Sintax error in init

* Thu May 06 2010 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 0.9-11mdv2010.1
+ Revision: 542720
- Rebuild

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - rise from the dead, there is a volonteer to maintain it

* Wed Apr 21 2010 Funda Wang <fwang@mandriva.org> 0.9-10mdv2010.1
+ Revision: 537357
- bump rel
- fix linkage

* Mon Mar 01 2010 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 0.9-9mdv2010.1
+ Revision: 512837
- Imspector as daemon

* Mon Mar 01 2010 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 0.9-8mdv2010.1
+ Revision: 512827
- P2 reddif
  add substitution into plugindir at imspector.conf to let non root users find libs

* Tue Feb 23 2010 Guillaume Rousse <guillomovitch@mandriva.org> 0.9-7mdv2010.1
+ Revision: 510416
- use rpm-helper macros to install ssl certificates
- apache configuration is a configuration file
- install directories with correct permissions directly
- switch default access policy to 'open to all'
- cleanup dependencies

* Wed Feb 17 2010 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 0.9-6mdv2010.1
+ Revision: 507049
- Rebuild
- S1 to begin as service, we need more work yet
- Description for sqlite sub-package  fixed

* Sun Feb 07 2010 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 0.9-3mdv2010.1
+ Revision: 501846
- P0 updated
- MySQL log support
  PostgreSQL log support
  SQLite log support
  SQLite message injection

* Wed Jan 20 2010 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 0.9-2mdv2010.1
+ Revision: 493937
- rely on filetrigger for reloading apache configuration begining with 2010.1, rpm-helper macros otherwise

* Mon Jul 27 2009 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 0.9-1mdv2010.0
+ Revision: 400890
- P1 rediff
- 0.9.0

* Thu Jul 16 2009 Funda Wang <fwang@mandriva.org> 0.8-5mdv2010.0
+ Revision: 396634
- drop database requires as they are not build by default

* Wed Jul 08 2009 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 0.8-4mdv2010.0
+ Revision: 393386
- P1+P4=P1
- again....
- P4 for gcc44
- again
- P3 added, multiple configuration lines is now possible like other unix configs

* Thu Mar 12 2009 Emmanuel Andry <eandry@mandriva.org> 0.8-3mdv2009.1
+ Revision: 354280
- create ssl certificate at install time
- add apache configuration

* Tue Mar 10 2009 Emmanuel Andry <eandry@mandriva.org> 0.8-2mdv2009.1
+ Revision: 353444
- import imspector


* Mon Mar  9 2009 Daniel Lucio <dlucio@okay.com.mx> 0.8-2mdv2009.1
- Addon of requires and buildrequieres
- CGI script
- SSL certificates install

* Fri Mar  6 2009 Daniel Lucio <dlucio@okay.com.mx> 0.8-1mdv2009.0
- First package

