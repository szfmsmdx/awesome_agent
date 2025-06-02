# awesome_agent

## 准备API KEY
更名 `.envtemplate` 文件为 `.env` 文件
替换该文件中相应的 api key 和地址

## 部署步骤
### 方法一
1. pip 安装相应的库文件
```py
# conda activate your_env
pip install -r requirements.txt
```

2. 起服务
```py
nohup python main.py > output.log 2>&1 &
cd frontend
python -m http.server 8080  # 或其他端口
```

3. 关闭服务
```py
lsof -i:7111    # 或其他端口，获取进程号
kill  xxxx      # kill 进程号

lsof -i:8080    # 结束前端进程
kill xxxx
```

### 方法二
25/6/2 添加 flask 支持  
在安装相关库后直接运行下列命令即可
```
python app.py
```
