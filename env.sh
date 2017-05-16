export SQLPATH=$PWD
export ORACLE_PATH=$PWD
export EDITOR=vi
export NLS_DATE_FORMAT='DD-MON-YYYY HH24:MI:SS'


alias s='rlwrap sqlplus / as sysdba'
alias opatch='$ORACLE_HOME/OPatch/opatch'
alias ss='$PWD/sqlcl/bin/sql'
alias rr='rlwrap rman'

showdb()
{
## - Below script will show Databases running on this server. DB name can be used to set the env.
## - Dependency on /etc/oratab | will remove leading "-" to handle alias issue with -MGMTDB
echo
for i in `ps -ef | egrep "mdb_smon|ora_smon|asm_smon" | grep -v grep | sed 's/^.*smon_//' | sort` ;
do
valias=`echo  $i | sed 's/-//'`
echo $valias
alias $valias="export ORAENV_ASK=NO; export ORACLE_SID=$i; . oraenv; export ORAENV_ASK=YES";
done
echo
}

showdb
