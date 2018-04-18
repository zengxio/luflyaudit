一、修改原生ssh代码，实现堡垒机
    过程:
        (1)、原生ssh的日志分析脚本讲解
        (2)、把用户交互脚本嵌入堡垒机
             创建单独的堡垒机程序账户，zxy，改下zxy用户的.bashrc,加入audit_shell.py调用
             用户登录zxy时，自动运行audit_shell.py
             确保自动退出zxy用户，logout。(在CTRL+C情况下也无法退出程序)
        (3)、解决日志输出路径的问题
             把程序路径传给session_tracker.sh脚本
             在session_tracker.sh脚本里面获取当前路径  (推荐)
        (4)、原生ssh无法解决传文件的监测
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

       5、编写分析日志脚本audit.py
       6、在普通用户下，一登陆就进入session_tracker脚本
          vi /home/zxy/.bashrc
              echo "......welome to luflu audit......"
              python /usr/local/luflyaudit/audit_shell.py

              如果遇到权限问题
              chown -R zxy:zxy /usr/local/luflyaudit/*
              chown -R zxy:zxy /usr/local/luflyaudit/


二、改paramiko源码。github ,demo/demo.py。（基于上面的结合完成）
    1、记录会话日志，创建数据库表
    2、把demo.py，嵌入到user_interactive.py脚本里

三、审计登录
    1、ssh命令行
    2、图像界面
    3、web ssh
    登录shellinabox无需认证登录
    4、django
        4.1选择要登录的机器，生成token(令牌、口令)
        4.2拿着口令到shellinabox那里
    5、shellinabox
        4.1提示用户输入口令
        4.2验证口令是否正确
                4.2.1如果正确，登录口令对应的机器
                4.2.2否则，禁止登录



web 开发模式
    1、mvc mtv
        好处：简单
        坏处：
            (1)、前后端耦合性高
            (2)、性能低
    2、前后端分离
       好处：开发效率高
             减轻了web框架独自创建渲染模块的压力




注意: 由于数据库sqllite 是用的utc时间。所以代码里面出现了time_obj = datetime.datetime.utcnow() - datetime.timedelta(seconds=300) 。
