# 0.说明
#### Dashboard For Business Services

```python
#文中所有$开头的均为变量，需要替换为实际环境下的真实值

—————————————————————————
|——README.md # 项目说明
|——manage.py # DJango管理文件
|——Sengladmin # Django工程目录
|——sengladmin # Django项目目录
|——prepares  # 准备数据
   |——python_module_code # 需要更新的Python模块源码文件
   |——static_data # 静态数据
   |——scripts # 脚本,Jenkins和build-docker等使用
|——requirements.txt # Python依赖包及版本
```


# 1.依赖
## 1.1 Redis
```python
https://redis.io/download #获取redis源码包安装
```

## 1.2 MongoDB
### 1.2.1 安装MongoDB
- Ubuntu下安装

```
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6

echo "deb [ arch=amd64,arm64,ppc64el,s390x ] http://repo.mongodb.com/apt/ubuntu xenial/mongodb-enterprise/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-enterprise.list

apt-get update

apt-get install -y mongodb-enterprise

service mongod start
```

- CentOS下安装

### 1.2.2 新建用户
```
mongo

use admin

db.createUser({user:"$root_name",pwd:"$root_pwd",roles:["userAdminAnyDatabase"]})

db.auth("$root_name","$root_pwd")

```

### 1.2.3 用户鉴权
```
use $user_db

db.createUser({user:"$user_name",pwd:"$user_pwd",roles:["readWrite"]})
```

### 1.2.4 修改授权登录配置
```
vim /etc/mongod.conf


#bindIp: 127.0.0.1

security:
  authorization: enabled
```

### 1.2.5 登录并验证
```
mongo

use $user_db

db.auth('$user_name', '$user_pwd')
```
或者
```
mongo mongodb://$user_name:$user_pwd@$mongo_ip:$mongo_port/$user_db
```

# 2.安装
## 2.1 创建虚拟环境目录
```
cd $workspace

mkdir $project-name

cd $project-name

virtualenv $venv-path-name
```

## 2.2 解压包
```
tar -zxvf $src.tar.gz
```

## 2.2 安装Python依赖模块
```
source $venv-path-name/bin/activate

pip install -r requirements.txt
```
## 2.3 修改部分模块源码
由于有些模块的源码不支持某些功能（也可能是没有正确使用）,需要用以下文件替换源文件
```
cp $workspace/$project-name/prepares/python_module_code/session.py $venv-path-name/lib/python2.7/site-packages/requests/sessions.py

cp $workspace/$project-name/prepares/python_module_code/base.py $venv-path-name/lib/python2.7/site-packages/consul/base.py

cp $workspace/$project-name/prepares/python_module_code/std.py $venv-path-name/lib/python2.7/site-packages/consul/std.py

cp $workspace/$project-name/prepares/python_module_code/mongodb.py $venv-path-name/lib/python2.7/site-packages/celery/backends/mongodb.py
```

## 2.3 修改配置文件
```python
$workspace/$project-name/Sengladmin/settings.py # 配置文件

LOGGING #日志的配置

CACHES #缓存的配置，这里使用的是Redis作为缓存

MONGODB #MongoDB的配置，Django使用

BROKER_URL #MongoDB的配置，Celery使用

CELERY_MONGODB_BACKEND_SETTINGS #MongoDB的配置，Celery使用

CELERYD_LOG_FILE #Celery的日志的配置 

MAIL_OUTBOX #邮件配置-发件箱

JENKINS_HOST #Jankins配置 - 服务地址

JENKINS_PORT #Jankins配置 - 服务端口

JENKINS_USER #Jankins配置 - 用户名

JENKINS_PASS #Jankins配置 - 密码

TEMPLATE_JENKINS_CONFIG_XML  #Jankins配置 - Jenkins配置模板 

JENKINS_BUILD_TRIGGER #Jenkins触发的编译脚本文件
```

## 2.4 导入静态数据
```
mongoimport -u $user_name -p $user_pwd -d $user_db -c $table --file=$workspace/$project-name/prepares/static_data/$table.json --jsonArray --pretty
```

# 3. 启动服务
## 3.1 启动Celery
```
nohup python manage.py celery worker >/dev/null 2>&1 &
```

## 3.2 启动Django
```
nohup python manage.py runserver 0.0.0.0:$port >/dev/null 2>&1 &
```

# 4. 使用
```
http://$server-ip:$server-port/sengladmin/

# 默认超级管理员用户: root
# 默认超级管理员密码: 123456
```
