1、python交互脚本里调用shell
   subprocess.run
2、实现检测 用户指令
   2.1 改源码，改不了
   2.2 strace
   2.3 strace 需要 唯一标识
   2.4 改ssh的参数处理的源码 -Z
        修改c代码之后
        while ((opt = getopt(ac, av, "1246ab:c:e:fgi:kl:m:no:p:qstvxz:"
           "ACD:E:F:GI:J:KL:MNO:PQ:R:S:TVw:W:XYyZ:")) != -1) { 加z:

        case 'Z':
             fprintf(stdout,"session_tag: %s\n" ,optarg);
             break;
        default 上面935
        ./configure 生成配置文件
        make 编译  (如需要改源码重新编译。需先执行make clean 再make &&  make install)
        make install 安装
   2.5 python 堡垒机脚本自动调用shell 会话脚本
       安装sshpass 实现自动输入登录密码
       ssh $ip -o StrictHostKeyChecking=no  自动填写yes,ssh连接参数
   2.6 starce 需要先拿到进程号，先让strace启动，循环等待ssh会话进程启动
   2.7 sudo strace 需要密码
       要更改sudoer配置文件，必须先切换到root  sudo bash，为了避免普通用户修改sudoer错误后，不能再使用sudo命令
       sudo vim /etc/sudoers
           %zxy  ALL=NOPASSWD:ALL
   3、会话监测日志，还要记录堡垒机账户，登录主机的账户，登录的主机ip
       创建SessionLog表，每次会话前创建一个sessionlog记录，把记录传给session_tracker.sh脚本
       因此，session_tracker.sh创建的会话日志，会以sessionlog.id 命名

   4、修复无法创建数据库，然后要删除数据库
    python manage.py migrate --fake #强制执行

   5、编写分析日志脚本
   6、在普通用户下，一登陆就进入session_tracker脚本
      vi /home/zxy/.bashrc
          echo "......welome to luflu audit......"
          python /usr/local/luflyaudit/audit_shell.py

          如果遇到权限问题
          chown -R zxy:zxy /usr/local/luflyaudit/*
          chown -R zxy:zxy /usr/local/luflyaudit/








