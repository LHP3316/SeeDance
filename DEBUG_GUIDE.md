# 调试指南

## 后端调试
- 查看日志: `tail -f logs/backend.log`
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 前端调试
- 查看日志: `tail -f logs/frontend.log`
- 前端地址: http://localhost:5173

## 常见问题
- 端口占用: 执行 `./stop` 清理
- 依赖缺失: `pip install -r requirements.txt`
