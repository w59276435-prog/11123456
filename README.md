# 企业级个人信息管理系统 v2.0

现代化、安全可靠的人员档案管理平台，支持完整的信息采集、审核、导出流程。

## 🎯 核心功能

### 用户端
- ✅ **多部分表单填报**：9大模块、100+个信息字段
- ✅ **草稿自动保存**：离线编辑、随时恢复
- ✅ **多规格证件照片**：7种分类上传、本地预览
- ✅ **关键信息加密**：身份证号、电话等敏感数据AES-256加密
- ✅ **实时状态跟踪**：草稿→待审核→已通过/已驳回

### 管理员端
- ✅ **人员审核管理**：待审核列表、详情查看、一键审核
- ✅ **全量数据导出**：Excel/CSV格式、支持筛选导出
- ✅ **用户权限管理**：创建/编辑/禁用用户、重置密码
- ✅ **完整审计日志**：所有操作记录、可追溯
- ✅ **统计分析**：草稿/待审核/已通过/已驳回数量统计

## 📊 信息结构（9大模块）

### 1. 基础身份&户籍（20个字段）
- 姓名、性别、民族、出生日期
- 身份证号、证件类型、有效期
- 籍贯、出生地、户口性质
- 现住址、临时地址、紧急联系地址

### 2. 联系方式（多条记录）
- 主/备手机号、固定电话
- 个人/工作邮箱
- 微信、QQ
- 紧急联系人（姓名、关系、电话）

### 3. 教育学业（学历+11条履历）
- 最高学历、学位、学习形式
- 学号、毕业证编号、学位证编号
- 教育履历：院校、专业、班级、校内职务

### 4. 家庭关系（直系+社会关系）
- 婚姻状况
- 家庭成员：父母、配偶、子女
- 社会关系：祖父母、兄妹、岳公婆等

### 5. 健康信息
- 身高、体重、血型、视力
- 既往病史、过敏史、残疾情况
- 疫苗接种、体检结论

### 6. 政治&党务（统战专项）
- 政治面貌、宗教信仰
- 入团/入党时间、转正时间
- 党团支部、人员类别
- 统战身份：侨胞、归侨、港澳台亲属

### 7. 设备&全网账号
- 移动设备：型号、IMEI、系统、绑定账号
- 网络设备：笔记本、台式机、平板
- 社交平台：微博、抖音、小红书、B站
- 办公平台：钉钉、企业微信
- 生活服务：支付宝、美团、滴滴
- 学习平台：学习通、智慧校园、网盘

### 8. 社会关系&奖惩政审
- 主要社会关系（8字段）
- 奖励记录、荣誉称号
- 违纪违法处分、技能证书
- 完整简历、违法犯罪记录

### 9. 工作从业&社保（在岗+履历）
- 现工作单位、部门、职务、入职时间
- 工作履历：历次工作经验
- 职业资质：资格证书、职称
- 社保状态、公积金、银行卡信息

## 🛠 技术栈

| 层次 | 技术 | 说明 |
|------|------|------|
| **后端** | FastAPI 0.115+ | 异步高效REST API |
| **ORM** | SQLAlchemy 2.0 | 类型安全的数据库映射 |
| **数据库** | SQLite/PostgreSQL | 本地/云端可选 |
| **前端** | HTML5 + Vue.js 3 | 现代化单页应用 |
| **加密** | cryptography | AES-256敏感数据加密 |
| **文件** | openpyxl + pandas | Excel/CSV导入导出 |
| **认证** | JWT + bcrypt | 安全的身份验证 |
| **部署** | Docker + Nginx | 容器化生产部署 |

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/w59276435-prog/11123456.git
cd 11123456
```

### 2. 环境配置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
cd backend
pip install -r requirements.txt

# 复制环境配置
cp .env.example .env
```

### 3. 初始化数据库

```bash
# 初始化数据库（自动创建表）
python -c "from app.database import init_db; init_db()"

# 创建默认管理员
python -c "from app.database import create_default_admin; create_default_admin()"
```

**默认管理员账号：**
- 用户名：`admin`
- 密码：`admin123`

### 4. 启动服务

```bash
# 启动 FastAPI 服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问应用

打开浏览器访问：

```
http://127.0.0.1:8000
```

API 文档 (Swagger UI)：

```
http://127.0.0.1:8000/docs
```

## 📖 API 文档

启动后自动生成 Swagger 文档，包含所有接口的完整定义和测试工具。

### 核心接口

#### 认证
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `POST /api/auth/change-password` - 修改密码

#### 个人信息
- `GET /api/person/self` - 获取自己的信息
- `POST /api/person/basic` - 保存基础信息
- `POST /api/person/education` - 保存教育信息
- `POST /api/person/work` - 保存工作信息
- `POST /api/person/family` - 保存家庭信息
- `POST /api/person/health` - 保存健康信息
- `POST /api/person/political` - 保存政治信息
- `POST /api/person/devices` - 保存设备/账号信息
- `POST /api/person/rewards` - 保存奖惩信息
- `POST /api/person/photos` - 上传证件照片
- `POST /api/person/submit` - 提交审核

#### 管理员
- `GET /api/admin/pending` - 获取待审核人员列表
- `GET /api/admin/person/{id}` - 获取人员详情
- `PATCH /api/admin/person/{id}/review` - 审核人员
- `GET /api/admin/users` - 获取用户列表
- `POST /api/admin/users` - 新增用户
- `PATCH /api/admin/users/{id}` - 编辑用户
- `DELETE /api/admin/users/{id}` - 删除用户

#### 导出
- `GET /api/export/excel` - 导出 Excel
- `GET /api/export/csv` - 导出 CSV

## 🔐 安全特性

✅ **敏感数据加密**
- 身份证号、电话等关键字段使用 AES-256 加密
- 加密密钥存储在环境变量中

✅ **密码安全**
- 使用 bcrypt 加盐哈希
- 密码最少 8 位，支持复杂度要求

✅ **访问控制**
- 基于角色的权限管理（RBAC）
- 用户只能编辑自己的信息
- 管理员操作完全审计日志

✅ **会话管理**
- JWT 令牌认证
- 自动超时登出
- 支持单设备登录限制

## 📁 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 应用入口
│   ├── config.py                  # 配置管理
│   ├── models.py                  # 9个 SQLAlchemy 数据模型
│   ├── schemas.py                 # Pydantic 请求/响应模型
│   ├── database.py                # 数据库初始化和连接
│   ├── security.py                # JWT 和加密工具
│   ├── api/
│   │   ├── auth.py               # 登录、注册、密码修改
│   │   ├── person.py             # 个人信息 API (9个模块)
│   │   ├── admin.py              # 审核、用户管理
│   │   └── export.py             # 导出 Excel/CSV
│   └── utils/
│       ├── crypto.py             # AES-256 加密/解密
│       ├── validators.py         # 数据验证
│       ├─�� excel_export.py       # Excel 导出
│       └── jwt_auth.py           # JWT 认证
├── requirements.txt
└── .env.example

frontend/
├── index.html                     # 主仪表板
├── login.html                     # 登录页
├── form.html                      # 9标签页表单
├── admin-dashboard.html           # 管理员仪表板
├── css/
│   ├── global.css                # 全局样式 + 主题色
│   ├── form.css                  # 表单组件样式
│   └── admin.css                 # 管理员样式
├── js/
│   ├── api.js                    # HTTP 请求封装
│   ├── auth.js                   # 认证逻辑
│   ├── form.js                   # 表单逻辑（9个模块）
│   ├── admin.js                  # 管理员逻辑
│   └── utils.js                  # 工具函数
└── assets/
    └── logo.png

docs/
├── API.md                         # API 详细文档
├── DATABASE.md                    # 数据库设计
├── INSTALL.md                     # 安装指南
├── DEPLOYMENT.md                  # 部署指南
└── SECURITY.md                    # 安全说明

docker-compose.yml                 # Docker 编排
Dockerfile
```

## 📊 性能指标

- **表单加载**: < 1s
- **搜索响应**: < 200ms
- **导出 1000 条**: < 3s
- **同时在线用户**: 500+ (SQLite) / 5000+ (PostgreSQL)

## 🐛 已知限制

- SQLite 最多支持同时 500 在线用户，生产环境建议使用 PostgreSQL
- 单次上传照片不超过 10MB
- 批量导入 CSV 最多 10000 条记录

## 🔄 升级计划

- [ ] 微信/钉钉登录集成
- [ ] 数据加密传输 (TLS)
- [ ] 短信通知
- [ ] 二维码扫描填表
- [ ] 数据备份和恢复
- [ ] 多语言支持
- [ ] 图表和报表

## 📞 技术支持

遇到问题？请提 Issue 或联系技术团队。

## 📄 许可证

MIT License

---

**最后更新**: 2026-06-07  
**版本**: 2.0  
**作者**: Personal Info Management Team