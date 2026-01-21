

# RUC Grade Monitor | 人大教务系统查分助手

> 基于 GitHub Actions 的中国人民大学（RUC）教务系统自动查分脚本。
> **无需服务器，无需挂机，自动识别验证码，出分即时邮件提醒。**

## 项目简介

期末出分季，还在每隔几分钟手动刷新教务系统？这个脚本可以帮你全自动完成查分任务。

本项目利用 `GitHub Actions` 实现云端 *24* 小时定时监控，通过 Python 脚本模拟登录教务系统，利用 `ddddocr` 自动识别验证码，并在发现新成绩时通过邮件（支持 QQ、163 等）第一时间通知你。

## 功能特性

* **云端运行**：依托 `GitHub Actions` ，无需购买服务器，无需电脑 24 小时开机。
* **自动打码**：集成 `ddddocr` 机器学习库，自动识别教务系统验证码。
* **邮件推送**：支持 *SMTP* 协议，新成绩直接推送到你的邮箱（推荐 QQ 邮箱）。

## Quick Start


### 第一步：Fork 本仓库

点击页面右上角的 **Fork** 按钮，将本项目复制到你自己的 `GitHub` 账号下。

### 第二步：配置隐私数据 (Secrets)

为了保护你的账号安全，请**不要**直接在代码里填写密码。我们需要使用 `GitHub Secrets` 。

1. 进入你 Fork 后的仓库页面。
2. 点击上方导航栏的 **Settings** -> 左侧栏 **Secrets and variables** -> **Actions**。
3. 点击 **New repository secret**，依次添加以下 5 个变量：

| 变量名 (Name) | 值 (Secret) | 说明 |
| --- | --- | --- |
| `STUDENT_ID` | `xxxxxxxxxx` | 你的学号 |
| `PASSWORD` | `你的密码` | 教务系统的登录密码 |
| `MAIL_USER` | `xxxx@qq.com` | 发送邮件的邮箱账号 |
| `MAIL_PASS` | `abcdefg...` | **邮箱授权码** |
| `RECEIVER` | `xxxx@qq.com` | 接收通知的邮箱 |

> [!NOTE]
> **如何获取 QQ 邮箱授权码 (`MAIL_PASS`)？**
> - 登录电脑版 QQ 邮箱 -> 设置 -> 账户。
> - 向下找到 "POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"。
> - 开启 "POP3/SMTP服务"。
> - 按照提示验证密保，获取一串英文代码，这就是授权码。


### 第三步：启用自动运行

1. 点击仓库上方的 **Actions** 标签。
2. 如果你看到一个绿色的按钮 "I understand my workflows, go ahead and enable them"，点击它。
3. 在左侧点击 **RUC Score Check**。
4. 点击右侧的 **Enable workflow**。

### 第四步：测试运行

1. 在 Actions 页面，点击左侧的 **RUC Score Check**
2. 点击右侧的 **Run workflow** 按钮,之后点击绿色的 **Run workflow**
3. 等待几十秒，如果出现 `✅` 绿色对号，且你的邮箱收到了一封“首次运行”或“新成绩”的邮件，说明配置成功
4. 之后脚本会每隔 30 分钟自动检查一次。

---

## 本地运行

如果你想在自己的电脑上运行或调试代码：

- **克隆仓库**
```bash
git clone https://github.com/JackXing875/RUC-Score.git
cd RUC-Score
```


- **安装依赖**
```bash
pip install -r requirements.txt
```


- **配置环境变量并运行**
你需要手动设置环境变量，或者直接临时修改代码中的变量进行测试。
```bash
# Windows PowerShell 示例
$env:STUDENT_ID="202xxxxx"
$env:PASSWORD="password"
# ... 设置其他变量 ...
python3 src/main.py
```



---

> [!WARNING]
> **免责声明**
> * 本项目仅供学习交流使用，**请勿用于任何商业用途**。
> * 开发者不对因使用本项目导致的任何账号安全问题或教务系统异常承担责任。
> * 请妥善保管好你的 `Secrets`，不要将密码分享给他人。


> [!IMPORTANT]
> 本项目参考了 *GitHub* 项目 [ruc-spider](https://github.com/Meteors27/ruc-spider)，特别感谢此项目！

---
最后，如果觉得本仓库有帮助，欢迎点亮⭐，这是对作者持续创作的最大鼓励！

