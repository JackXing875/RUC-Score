import os
import json
import logging
import smtplib
from email.mime.text import MIMEText
from script import RucScore

# 环境变量
STUDENT_ID = os.environ.get("STUDENT_ID")
PASSWORD = os.environ.get("PASSWORD")
MAIL_USER = os.environ.get("MAIL_USER")
MAIL_PASS = os.environ.get("MAIL_PASS")
RECEIVER = os.environ.get("RECEIVER")

class JwSpider(RucScore):
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
        RucScore.login(self)
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
            raise e 

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    if not all([STUDENT_ID, PASSWORD, MAIL_USER, MAIL_PASS]):
        logging.error("请在 GitHub Secrets 中配置完整的环境变量！")
        exit(1)

    spider = JwSpider(STUDENT_ID, PASSWORD)
    messager = EmailMessager()

    try:
        logging.info("开始登录...")
        spider.login()
        current_data = spider.getScore()
        
        current_scores_map = {}
        for item in current_data:
            c_name = item.get("kcname")
            
            if not c_name:
                continue

            c_detail = f"总分:{item.get('zcjname1')} (平时:{item.get('cjxm1')} / 期末:{item.get('cjxm3')})"
            current_scores_map[c_name] = c_detail

        old_scores_map = {}
        if os.path.exists("scores.json"):
            with open("scores.json", "r", encoding="utf-8") as f:
                old_scores_map = json.load(f)
        else:
            logging.info("首次运行，未发现历史记录。")

        updates = [] 
        for name, detail in current_scores_map.items():
            if name not in old_scores_map:
                updates.append(f"【新成绩】{name}\n{detail}")
            elif old_scores_map[name] != detail:
                updates.append(f"【更新】{name}\n原：{old_scores_map[name]}\n新：{detail}")

        if updates:
            email_title = f"【成绩提醒】发现 {len(updates)} 条新动态"
            email_body = "同学你好，监测到以下成绩变动：\n\n" + "\n------------------\n".join(updates)
            
            messager.send(email_title, email_body)
            
            with open("scores.json", "w", encoding="utf-8") as f:
                json.dump(current_scores_map, f, ensure_ascii=False, indent=2)
            logging.info("成绩记录已更新并保存。")
        
        else:
            if not os.path.exists("scores.json"):
                with open("scores.json", "w", encoding="utf-8") as f:
                    json.dump(current_scores_map, f, ensure_ascii=False, indent=2)
                logging.info("首次运行初始化完成（无邮件发送）。")
            else:
                logging.info("没有新成绩，无需更新。")

    except Exception as e:
        logging.error(f"运行出错: {e}")
        exit(1)
