from resource_management import *
import functions


class HbaseServiceCheck(Script):
  def perform(self, env):
    import params
    env.set_params(params)
    
    output_file = "/apps/hbase/data/ambarismoketest"
    test_cmd = format("fs -test -e {output_file}")
    kinit_cmd = format("{kinit_path_local} -kt {smoke_user_keytab} {smoke_test_user};") if params.security_enabled else ""
    hbase_servicecheck_file = '/tmp/hbase-smoke.sh'
  
    File( '/tmp/hbaseSmokeVerify.sh',
      content = StaticFile("hbaseSmokeVerify.sh"),
      mode = 0755
    )
  
    File( hbase_servicecheck_file,
      mode = 0755,
      content = Template('hbase-smoke.sh.j2')
    )
    
    if params.security_enabled:    
      hbase_grant_premissions_file = '/tmp/hbase_grant_permissions.sh'
      hbase_kinit_cmd = format("{kinit_path_local} -kt {hbase_user_keytab} {hbase_user};")
      grantprivelegecmd = format("{hbase_kinit_cmd} hbase shell {hbase_grant_premissions_file}")
  
      File( hbase_grant_premissions_file,
        owner   = params.hbase_user,
        group   = params.user_group,
        mode    = 0644,
        content = Template('hbase_grant_permissions.j2')
      )
      
      Execute( grantprivelegecmd,
        user = params.hbase_user,
      )

    servicecheckcmd = format("{kinit_cmd} hbase --config {conf_dir} shell {hbase_servicecheck_file}")
    smokeverifycmd = format("{kinit_cmd} /tmp/hbaseSmokeVerify.sh {conf_dir} {service_check_data}")
  
    Execute( servicecheckcmd,
      tries     = 3,
      try_sleep = 5,
      user = params.smoke_test_user,
      logoutput = True
    )
  
    Execute ( smokeverifycmd,
      tries     = 3,
      try_sleep = 5,
      user = params.smoke_test_user,
      logoutput = True
    )
    
def main():
  import sys
  command_type = 'perform'
  command_data_file = '/root/workspace/HBase/input.json'
  basedir = '/root/workspace/HBase/main'
  sys.argv = ["", command_type, command_data_file, basedir]
  
  HbaseServiceCheck().execute()
  
if __name__ == "__main__":
  HbaseServiceCheck().execute()
  
