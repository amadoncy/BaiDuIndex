# 百度指数数据采集与分析工具

这是一个功能强大的百度指数数据采集与分析平台，支持多地区、多关键词的数据采集，提供数据可视化、数据预测和人群画像分析，同时具备完善的用户管理系统。

## 功能特点

- 支持全国、区域、省份、城市级别的数据采集
- 自动登录百度指数平台
- 支持多关键词数据采集
- 数据自动保存到Excel和本地数据库
- 人群画像分析功能
- 数据预测与趋势分析
- 数据可视化展示
- 支持本地天气信息获取
- 用户注册、登录和密码重置系统
- 支持断点续传，自动补充缺失数据
- 内置完整的城市编码系统
- 内存优化，支持大数据量处理
- 异常处理和自动重试机制

## 系统要求

- Python 3.7+
- Chrome浏览器（用于自动登录）
- 本地数据库（mysql）

## 安装步骤

1. 克隆项目到本地：
```bash
git clone [项目地址]
cd BaiDuIndex
```

2. 安装依赖包：
```bash
pip install -r requirements.txt
```

3. 配置用户信息：
   - 在 `resources/user_info.txt` 中配置百度账号信息（可选）
   - 或通过系统注册功能创建本地账号

## 目录结构

```
BaiDuIndex/
├── cache/              # 缓存文件目录
├── config/             # 配置文件目录
│   ├── city_codes.py   # 城市编码配置
│   ├── database.py     # 数据库配置
│   └── user_config.py  # 用户配置
├── data/               # 数据存储目录
│   └── trend/          # 趋势数据存储
├── gui/                # 图形界面相关代码
│   ├── loginwindow.py          # 登录窗口
│   ├── main_window.py          # 主界面
│   ├── data_display_window.py  # 数据展示窗口
│   ├── register_window.py      # 注册窗口
│   ├── reset_password_window.py# 密码重置窗口
│   └── chart_widget.py         # 图表组件
├── resources/          # 资源文件目录
├── sql/                # SQL相关文件
├── utils/              # 工具函数目录
│   ├── get_trend_utils.py           # 趋势数据获取
│   ├── get_crowd_portrait_utils.py  # 人群画像获取
│   ├── data_prediction_utils.py     # 数据预测
│   ├── get_index_cookie_utils.py    # Cookie管理
│   ├── get_local_weather_utils.py   # 天气信息获取
│   ├── db_utils.py                  # 数据库操作
│   ├── captcha_utils.py             # 验证码处理
│   └── validation_utils.py          # 数据验证
├── main.py             # 主程序入口
└── requirements.txt    # 项目依赖
```

## 使用方法

1. 运行主程序：
```bash
python main.py
```

2. 登录系统：
   - 使用已有账号登录
   - 或注册新账号
   - 忘记密码可通过密码重置功能

3. 数据采集：
   - 选择要采集的地区（全国/区域/省份/城市）
   - 输入要采集的关键词
   - 选择时间范围
   - 点击开始采集

4. 数据分析：
   - 查看趋势图表和数据可视化
   - 使用人群画像功能分析用户特征
   - 应用数据预测功能进行趋势预测

5. 数据存储：
   - Excel文件保存在 `data/trend/` 目录下
   - 数据自动存储到本地数据库

## 技术栈

- PyQt5: 图形界面开发
- Selenium: 网页自动化
- Pandas: 数据处理
- PyEcharts: 数据可视化
- TensorFlow: 数据预测模型
- Scikit-learn: 机器学习算法
- SQLite: 本地数据存储

## 注意事项

1. 首次使用需要手动完成登录验证
2. 建议使用稳定的网络连接
3. 大量数据采集时注意内存使用
4. 请遵守百度指数的使用条款和限制

## 常见问题

1. 登录失败
   - 检查账号密码是否正确
   - 确认网络连接正常
   - 可能需要手动完成验证码

2. 数据获取失败
   - 检查cookies是否有效
   - 确认网络连接正常
   - 查看日志文件了解详细错误信息

3. 程序崩溃
   - 检查依赖包是否完整安装
   - 确认Python版本兼容性
   - 尝试重启应用

## 更新日志

### v2.0.0
- 增加数据预测功能
- 增加人群画像分析
- 优化用户界面
- 新增本地用户系统

### v1.0.0
- 初始版本发布
- 支持基本的指数数据采集功能
- 提供图形界面操作

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。

## 许可证

本项目采用 MIT 许可证