
-- User Creation

groupadd -g 54321 oinstall
groupadd -g 54322 dba
groupadd -g 54323 oper
groupadd -g 54324 backupdba
groupadd -g 54325 dgdba
groupadd -g 54326 kmdba
groupadd -g 54327 asmdba
groupadd -g 54328 asmoper
groupadd -g 54329 asmadmin

useradd -u 54321 -g oinstall -G dba,oper oracle

-- Directory Created

mkdir -p /u01/app/oracle/product/12.1.0.2/db_1
chown -R oracle:oinstall /u01
chmod -R 775 /u01


-------------------------------------------- Bash Profile

# Oracle Settings
export TMP=/tmp
export TMPDIR=$TMP

export ORACLE_HOSTNAME=
export ORACLE_UNQNAME=
export ORACLE_BASE=/u01/app/oracle
export ORACLE_HOME=$ORACLE_BASE/product/12.1.0.2/db_1
export ORACLE_SID=cdb1

export PATH=/usr/sbin:$PATH
export PATH=$ORACLE_HOME/bin:$PATH

export LD_LIBRARY_PATH=$ORACLE_HOME/lib:/lib:/usr/lib
export CLASSPATH=$ORACLE_HOME/jlib:$ORACLE_HOME/rdbms/jlib


showdb()
{
## - Below script will show Databases running on this server. DB name can be used to set the env.
## - Dependency on /etc/oratab | will remove leading "-" to handle alias issue with -MGMTDB
echo
for i in `ps -ef | egrep "mdb_smon|ora_smon|asm_smon" | grep -v egrep | sed 's/^.*smon_//' | sort` ;
do
valias=`echo  $i | sed 's/-//'`
echo $valias
alias $valias="export ORAENV_ASK=NO; export ORACLE_SID=$i; . oraenv";
done
echo
}
showdb

alias s=' export ORAENV_ASK=NO; . oraenv; rlwrap sqlplus / as sysdba'
alias r=' rlwrap rman target / '

