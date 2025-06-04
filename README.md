# awesome_agent

## 准备API KEY
更名 `.envtemplate` 文件为 `.env` 文件
替换该文件中相应的 api key 和地址

## 部署
在安装相关库后直接运行下列命令即可  
(建议关闭 flask 的debug模式, 即app.py文件中将debug改为False)
```
nohup python app.py > output.log 2>&1 &

# 关闭服务
lsof -i:7111 # 或者自定义的端口
kill xxxx    # kill 掉该端口号
```
