#!/bin/sh
export LANG="zh_CN.UTF-8"

# start or stop or restart
optype=$1

# 修改此处启动程序名 start_name
start_name="redis_tools"
project_file=$(cd $(dirname $0) && pwd )
log_file="$project_file/$start_name.log"
PROGNAME="$project_file/$start_name.py"



if [ x"${optype}" = x ] ; then
    optype=start
fi

function start()
{
    # 进程数量
    prog_num=`ps -ef | grep $PROGNAME | grep -v grep | wc -l`
    if [ $prog_num -eq 0 ] ; then
        echo "start $PROGNAME"
        nohup python3 -u $PROGNAME >> $log_file 2>&1 &
    else
        echo "$PROGNAME is started"
    fi
}

function stop()
{
    # 进程数量
    prog_num=`ps -ef | grep $PROGNAME | grep -v grep | wc -l`
    if [ $prog_num -eq 0 ] ; then
      echo "$PROGNAME is stopped"
      return
    fi

    # 查出所有进程 id
    prog_ids=`ps -ef | grep $PROGNAME | grep -v grep | awk '{print $2}'`

    for pid in $prog_ids;
    do
        kill -9 $pid;
    done
    echo "stop $PROGNAME"
}
case "$optype" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 1
        start
        ;;
    *)
        echo "Only support start|stop|restart"
        exit 1
esac


