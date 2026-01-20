import os
import json
import logging
import smtplib
import time
from email.mime.text import MIMEText
from RUC_Spider import RucSpider

# --- 从环境变量获取配置 (GitHub Secrets) ---
# 这样你的密码就不会暴露在代码里
STUDENT_ID = os.environ.get("STUDENT_ID")
PASSWORD = os.environ.get("PASSWORD")
MAIL_USER = os.environ.get("MAIL_USER")
MAIL_PASS = os.environ.get("MAIL_PASS")
RECEIVER = os.environ.get("RECEIVER") # 接收邮箱，通常等于 MAIL_USER

class JwSpider(RucSpider):
    scoreURL = "https://jw.ruc.edu.cn/resService/jwxtpt/v1/xsd/cjgl_xsxdsq/findKccjList"

    def __init__(self, username, password):
        super(JwSpider, self).__init__(username, password)
        self.__json = {
            "pyfa007id": "1", "jczy013id": [], "fxjczy005id": "", "cjckflag": "xsdcjck",
            "page": {"pageIndex": 1, "pageSize": 30, "orderBy": '[{"field":"jczy013id","sortType":"asc"}]',
                     "conditions": "QZDATASOFTJddJJVIJY29uZGl0aW9uR3JvdXAlMjIlM0ElNUIlN0IlMjJsaW5rJTIyJTNBJTIyYW5kJTIyJTJDJTIyY29uZGl0aW9uJTIyJTNBJTVCJTVEJTdEyTTECTTE"},
        }
        self.__params = {"resourceCode": "XSMH0526", "apiCode": "jw.xsd.xsdInfo.controller.CjglKccjckController.findKccjList"}
        self.__headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
            "TOKEN": "", "Accept": "application/json, text/plain, */*",
        }

    def login(self):
        RucSpider.login(self)
        self.__headers["TOKEN"] = self.sess.cookies["token"]

    def getScore(self):
        try:
            self.res = self.sess.post(self.scoreURL, headers=self.__headers, params=self.__params, json=self.__json)
            json_data = self.res.json()
            if json_data["errorCode"] != "success":
                raise Exception(json_data["errorCode"])
            return json_data["data"]
        except Exception as e:
            logging.error(f"Error getting score: {str(e)}")
            raise e

class EmailMessager:
    def send(self, title, content):
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = title
        msg['From'] = MAIL_USER
        msg['To'] = RECEIVER
        try:
            s = smtplib.SMTP_SSL("smtp.qq.com", 465)
            s.login(MAIL_USER, MAIL_PASS)
            s.sendmail(MAIL_USER, RECEIVER, msg.as_string())
            s.quit()
            logging.info(f"邮件发送成功: {title}")
        except Exception as e:
            logging.error(f"邮件发送失败: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    # 1. 检查环境变量是否配置
    if not all([STUDENT_ID, PASSWORD, MAIL_USER, MAIL_PASS]):
        logging.error("请在 GitHub Secrets 中配置完整的环境变量！")
        exit(1)

    spider = JwSpider(STUDENT_ID, PASSWORD)
    messager = EmailMessager()

    try:
        logging.info("开始登录...")
        spider.login()
        current_data = spider.getScore()
        
        # 整理当前成绩为字典格式 {课程名: 详细信息}
        current_scores_map = {}
        for item in current_data:
            c_name = item.get("kcname")
            # 组合一个唯一的成绩字符串，包含平时、期末、总分
            c_detail = f"总分:{item.get('zcjname1')} (平时:{item.get('cjxm1')} / 期末:{item.get('cjxm3')})"
            current_scores_map[c_name] = c_detail

        # 2. 读取上次保存的成绩 (scores.json)
        old_scores_map = {}
        if os.path.exists("scores.json"):
            with open("scores.json", "r", encoding="utf-8") as f:
                old_scores_map = json.load(f)
        else:
            logging.info("首次运行，未发现历史记录，将建立基准文件。")

        # 3. 对比并发送通知
        new_updates = False
        for name, detail in current_scores_map.items():
            if name not in old_scores_map:
                # 完全是新课
                messager.send(f"【新成绩发布】{name}", f"课程：{name}\n{detail}")
                new_updates = True
            elif old_scores_map[name] != detail:
                # 课程存在，但分数变了（比如录入了期末分）
                messager.send(f"【成绩更新】{name}", f"课程：{name}\n原状态：{old_scores_map[name]}\n新状态：{detail}")
                new_updates = True

        # 4. 如果有更新，保存新的 json 文件
        # 注意：这里我们只保存，GitHub Actions 的 YAML 脚本负责把这个文件 push 回仓库
        if new_updates or not os.path.exists("scores.json"):
            with open("scores.json", "w", encoding="utf-8") as f:
                json.dump(current_scores_map, f, ensure_ascii=False, indent=2)
            logging.info("成绩记录已更新。")
        else:
            logging.info("没有新成绩，无需更新文件。")

    except Exception as e:
        logging.error(f"运行出错: {e}")
        # 出错不发邮件，只打印日志，避免半夜把 Action 搞崩
        exit(1)