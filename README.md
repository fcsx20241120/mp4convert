# MP4 视频上传与转换工具

基于 Flask + Vue.js 的视频文件上传和格式转换工具，支持将非 H.264 编码的视频转换为标准 H.264 格式。

## 功能特性

- 📁 **文件上传** - 支持点击或拖拽上传 MP4 文件
- 📊 **文件信息** - 自动解析视频编码、分辨率、时长等信息
- 🔄 **格式转换** - 非 H.264 编码视频可一键转换为标准 H.264 格式
- 📈 **进度显示** - 实时显示上传和转换进度
- 💻 **前端界面** - 简洁美观的 Vue.js 界面

## 技术栈

- **后端**: Flask 3.0.0 + Flask-CORS
- **前端**: Vue.js 3.4.21
- **视频处理**: FFmpeg (libx264 + AAC)

## 环境要求

- Python 3.8+
- FFmpeg (已安装并配置到环境变量)

## 安装步骤

1. 克隆项目
```bash
git clone https://github.com/fcsx20241120/mp4convert.git
cd mp4convert
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 启动服务
```bash
python app.py
```

4. 访问 http://127.0.0.1:5000

## 项目结构

```
mp4convert/
├── app.py              # Flask 后端应用
├── index.html          # Vue 前端页面
├── requirements.txt    # Python 依赖
├── .gitignore         # Git 忽略配置
├── uploads/           # 上传文件目录 (自动创建)
└── README.md          # 项目说明
```

## API 接口

### 上传视频
- **URL**: `/upload`
- **方法**: `POST`
- **参数**: `file` (MP4 文件)
- **响应**: 文件信息（名称、大小、编码、分辨率、时长等）

### 转换视频
- **URL**: `/convert`
- **方法**: `POST`
- **参数**: `file` (MP4 文件)
- **响应**: 转换后的文件信息

## 转换参数

- 视频编码：H.264 (libx264)
- 音频编码：AAC (128kbps)
- CRF 质量：23
- 预设：medium

## 注意事项

1. 默认最大上传文件大小为 2GB
2. 上传的文件保存在 `uploads/` 目录
3. 转换完成后会删除原始文件
4. Windows 系统需确保 FFmpeg 已正确安装

## License

MIT
