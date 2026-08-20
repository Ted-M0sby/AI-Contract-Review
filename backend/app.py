from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid
import re
import pymysql
import fastapi
import random
import smtplib
import os
from html import escape
from email.mime.text import MIMEText
from email.header import Header
from fastapi import FastAPI, Request
from dotenv import load_dotenv
import hashlib
import fitz
import requests
from docx import Document
from fastapi import FastAPI, Request, UploadFile, File, Form
load_dotenv(override=True)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],   # 请求方法，允许所有
    allow_headers=["*"],   # 请求头，允许所有
    expose_headers=["*"],  # 响应头，允许所有
)

def mysql():
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='Aa123456',
        database='contract',  # 库名
        port=3306,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor  # 当查询数据时，以字典形式返回（默认元组）
    )
    return conn

def send_review_done_email(to_email,contract_title,contract_id):
    qq_email=os.getenv('QQ_EMAIL')
    qq_auth_code=os.getenv('QQ_AUTH_CODE')
    if not qq_email or not qq_auth_code or not to_email:
        print('审查完成邮件未发送：邮箱配置或收件人缺失')
        return False
    safe_title=escape(contract_title or '合同')
    safe_contract_id=escape(str(contract_id))
    content=f"""
    <div style="font-family:Arial,sans-serif;background:#f5f7fa;padding:30px;">
        <div style="max-width:520px;margin:auto;background:#ffffff;border-radius:12px;padding:30px;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
            <h2 style="margin:0 0 20px;color:#1f2937;">合同审查系统</h2>
            <p style="color:#4b5563;font-size:15px;">你好，你提交的合同已经完成 AI 审查。</p>
            <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;padding:16px;margin:18px 0;">
                <p style="margin:0 0 8px;color:#6b7280;font-size:14px;">合同名称</p>
                <p style="margin:0;color:#1f2937;font-size:18px;font-weight:bold;">{safe_title}</p>
                <p style="margin:12px 0 0;color:#6b7280;font-size:13px;">合同 ID：{safe_contract_id}</p>
            </div>
            <p style="color:#4b5563;font-size:15px;">请登录系统查看完整审查结果、风险条款和修改建议。</p>
            <hr style="border:none;border-top:1px solid #e5e7eb;margin:25px 0;">
            <p style="color:#9ca3af;font-size:12px;">如果不是你本人操作，请忽略此邮件。</p>
        </div>
    </div>
    """
    message=MIMEText(content,'html','utf-8')
    message['From']=qq_email
    message['To']=to_email
    message['Subject']=Header('合同审查完成通知','utf-8')
    try:
        smtp=smtplib.SMTP_SSL('smtp.qq.com',465,timeout=20)
        smtp.login(qq_email,qq_auth_code)
        result=smtp.sendmail(qq_email,[to_email],message.as_string())
        print('审查完成邮件发送结果：',result)
        smtp.quit()
        return True
    except Exception as e:
        print('审查完成邮件发送失败：',e)
        return False

class EmailData(BaseModel):
    email:str

class RegisterData(BaseModel):
    email:str
    password:str
    code:str

class LoginData(BaseModel):
    email:str
    password:str

class ReviewData(BaseModel):
    user_id:int
    review_perspective:str='neutral'

class DingTalkData(BaseModel):
    user_id:int

@app.post('/auth/send-code')
async def send_code(data:EmailData):
    if not data.email.endswith('@qq.com'):
        return {'code':400,'message':'请输入QQ邮箱'}
    code=str(random.randint(100000,999999))
    conn=mysql()
    cursor=conn.cursor()
    cursor.execute('DELETE FROM email_codes WHERE email=%s',(data.email,))
    cursor.execute('INSERT INTO email_codes(email,code) VALUES(%s,%s)',(data.email,code))
    conn.commit()
    cursor.close()
    conn.close()
    qq_email=os.getenv('QQ_EMAIL')
    qq_auth_code=os.getenv('QQ_AUTH_CODE')
    content=f"""
    <div style="font-family:Arial,sans-serif;background:#f5f7fa;padding:30px;">
        <div style="max-width:520px;margin:auto;background:#ffffff;border-radius:12px;padding:30px;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
            <h2 style="margin:0 0 20px;color:#1f2937;">合同审查系统</h2>
            <p style="color:#4b5563;font-size:15px;">你好，你正在注册 AI 合同审查系统。</p>
            <p style="color:#4b5563;font-size:15px;">你的验证码是：</p>
            <div style="font-size:32px;font-weight:bold;letter-spacing:8px;color:#2563eb;text-align:center;padding:20px 0;">
                {code}
            </div>
            <p style="color:#6b7280;font-size:14px;">验证码 5 分钟内有效，请勿泄露给他人。</p>
            <hr style="border:none;border-top:1px solid #e5e7eb;margin:25px 0;">
            <p style="color:#9ca3af;font-size:12px;">如果不是你本人操作，请忽略此邮件。</p>
        </div>
    </div>
    """
    message=MIMEText(content,'html','utf-8')
    message['From']=qq_email
    message['To']=data.email
    message['Subject']=Header('合同审查系统注册验证码','utf-8')
    try:
        smtp=smtplib.SMTP_SSL('smtp.qq.com',465)
        smtp.login(qq_email,qq_auth_code)
        result=smtp.sendmail(qq_email,[data.email],message.as_string())
        print("邮件发送结果：",result)
        smtp.quit()
        return {'code':200,'message':'验证码发送成功'}
    except Exception as e:
        return {'code':500,'message':'验证码发送失败','error':str(e)}

@app.post('/auth/register')
async def register(data:RegisterData):
    conn=mysql()
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email=%s',(data.email,))
    user=cursor.fetchone()
    if user:
        cursor.close()
        conn.close()
        return {'code':400,'message':'邮箱已注册'}
    cursor.execute('SELECT * FROM email_codes WHERE email=%s AND created_at>=NOW()-INTERVAL 5 MINUTE ORDER BY id DESC LIMIT 1',(data.email,))
    email_code=cursor.fetchone()
    if not email_code:
        cursor.close()
        conn.close()
        return {'code':400,'message':'验证码不存在或已过期'}
    if email_code['code']!=data.code:
        cursor.close()
        conn.close()
        return {'code':400,'message':'验证码错误'}
    cursor.execute('INSERT INTO users(email,password) VALUES(%s,%s)',(data.email,data.password))
    conn.commit()
    user_id=cursor.lastrowid
    cursor.execute('DELETE FROM email_codes WHERE email=%s',(data.email,))
    conn.commit()
    cursor.close()
    conn.close()
    return {'code':200,'message':'注册成功','user_id':user_id,'email':data.email}

@app.post('/auth/login')
async def login(data:LoginData):
    conn=mysql()
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email=%s AND password=%s',(data.email,data.password))
    user=cursor.fetchone()
    cursor.close()
    conn.close()
    if not user:
        return {'code':400,'message':'邮箱或密码错误'}
    return {'code':200,'message':'登录成功','user_id':user['id'],'email':user['email']}

@app.post('/contracts/upload')
async def upload_contract(user_id:int=Form(...),title:str=Form(...),contract_type:str=Form(...),file:UploadFile=File(...)):
    conn=mysql()
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id=%s',(user_id,))
    user=cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        return {'code':400,'message':'用户不存在'}
    filename=file.filename
    file_type=filename.split('.')[-1].lower()
    if file_type not in ['pdf','docx','txt']:
        cursor.close()
        conn.close()
        return {'code':400,'message':'目前只支持PDF、DOCX、TXT文件'}
    upload_dir='uploads'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    save_name=str(uuid.uuid4())+'.'+file_type
    file_path=os.path.join(upload_dir,save_name)
    content=await file.read()
    with open(file_path,'wb') as f:
        f.write(content)
    raw_text=''
    try:
        if file_type=='pdf':
            pdf=fitz.open(file_path)
            for page in pdf:
                raw_text=raw_text+page.get_text()+'\n'
            pdf.close()
        elif file_type=='docx':
            doc=Document(file_path)
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    raw_text=raw_text+paragraph.text.strip()+'\n'
        elif file_type=='txt':
            try:
                raw_text=content.decode('utf-8')
            except:
                raw_text=content.decode('gbk')
    except Exception as e:
        cursor.close()
        conn.close()
        return {'code':500,'message':'合同解析失败','error':str(e)}
    raw_text=raw_text.strip()
    cleaned_text=raw_text
    content_hash=hashlib.sha256(cleaned_text.encode('utf-8')).hexdigest()
    sql='''INSERT INTO contracts
    (user_id,title,contract_type,original_filename,file_type,file_path,raw_text,cleaned_text,content_hash,status)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    cursor.execute(sql,(user_id,title,contract_type,filename,file_type,file_path,raw_text,cleaned_text,content_hash,'pending'))
    conn.commit()
    contract_id=cursor.lastrowid
    cursor.close()
    conn.close()
    return {'code':200,'message':'合同上传成功','contract_id':contract_id,'title':title,'contract_type':contract_type,'status':'pending'}

@app.get('/contracts')
async def get_contracts(user_id:int):
    conn=mysql()
    cursor=conn.cursor()
    cursor.execute('SELECT id,title,contract_type,status,overall_risk,created_at FROM contracts WHERE user_id=%s ORDER BY id DESC',(user_id,))
    contracts=cursor.fetchall()
    cursor.close()
    conn.close()
    for item in contracts:
        if item['contract_type']=='housing_lease':
            item['contract_type_name']='房屋租赁合同'
    return {'code':200,'message':'查询成功','data':contracts}

@app.get('/contracts/{contract_id}')
async def get_contract(contract_id:int,user_id:int):
    conn=mysql()
    cursor=conn.cursor()
    cursor.execute('SELECT id,user_id,title,contract_type,original_filename,file_type,status,overall_risk,cleaned_text,raw_text,created_at FROM contracts WHERE id=%s AND user_id=%s',(contract_id,user_id))
    contract=cursor.fetchone()
    cursor.close()
    conn.close()
    if not contract:
        return {'code':404,'message':'合同不存在'}
    if contract['contract_type']=='housing_lease':
        contract['contract_type_name']='房屋租赁合同'
    if contract['cleaned_text']:
        contract['content']=contract['cleaned_text']
    else:
        contract['content']=contract['raw_text']
    contract.pop('cleaned_text',None)
    contract.pop('raw_text',None)
    return {'code':200,'message':'查询成功','data':contract}

@app.post('/contracts/{contract_id}/review')
async def review_contract(contract_id:int,data:ReviewData):
    conn=mysql()
    cursor=conn.cursor()
    cursor.execute('SELECT * FROM contracts WHERE id=%s AND user_id=%s',(contract_id,data.user_id))
    contract=cursor.fetchone()
    if not contract:
        cursor.close()
        conn.close()
        return {'code':404,'message':'合同不存在'}
    cursor.execute('SELECT email FROM users WHERE id=%s',(data.user_id,))
    user=cursor.fetchone()
    user_email=user['email'] if user else None
    if contract['cleaned_text']:
        contract_text=contract['cleaned_text']
    else:
        contract_text=contract['raw_text']
    if not contract_text:
        cursor.close()
        conn.close()
        return {'code':400,'message':'合同没有可审查文本'}
    cursor.execute('UPDATE contracts SET status=%s,review_error=NULL WHERE id=%s AND user_id=%s',('reviewing',contract_id,data.user_id))
    conn.commit()
    dify_base_url=os.getenv('DIFY_BASE_URL')
    dify_api_key=os.getenv('DIFY_API_KEY')
    try:
        response=requests.post(
            dify_base_url+'/workflows/run',
            headers={
                'Authorization':'Bearer '+dify_api_key,
                'Content-Type':'application/json'
            },
            json={
                'inputs':{
                    'contract_text':contract_text,
                    'contract_type':contract['contract_type'],
                    'review_perspective':data.review_perspective
                },
                'response_mode':'blocking',
                'user':'user_'+str(data.user_id)
            },
            timeout=900
        )
        result=response.json()
        if response.status_code!=200:
            cursor.execute('UPDATE contracts SET status=%s,review_error=%s WHERE id=%s AND user_id=%s',('failed',json.dumps(result,ensure_ascii=False),contract_id,data.user_id))
            conn.commit()
            cursor.close()
            conn.close()
            return {'code':500,'message':'Dify调用失败','error':result}
        if result.get('data',{}).get('status')!='succeeded':
            cursor.execute('UPDATE contracts SET status=%s,review_error=%s WHERE id=%s AND user_id=%s',('failed',json.dumps(result,ensure_ascii=False),contract_id,data.user_id))
            conn.commit()
            cursor.close()
            conn.close()
            return {'code':500,'message':'合同审查失败','error':result}
        review_result=result.get('data',{}).get('outputs',{}).get('result')
        if isinstance(review_result,str):
            review_result=json.loads(review_result)
        overall_risk=review_result.get('overall_risk','low')
        cursor.execute('UPDATE contracts SET status=%s,overall_risk=%s,review_result=%s,review_error=NULL,reviewed_at=NOW() WHERE id=%s AND user_id=%s',('reviewed',overall_risk,json.dumps(review_result,ensure_ascii=False),contract_id,data.user_id))
        conn.commit()
        send_review_done_email(user_email,contract['title'],contract_id)
        cursor.close()
        conn.close()
        return {'code':200,'message':'合同审查成功','contract_id':contract_id,'status':'reviewed','data':review_result}
    except Exception as e:
        cursor.execute('UPDATE contracts SET status=%s,review_error=%s WHERE id=%s AND user_id=%s',('failed',str(e),contract_id,data.user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return {'code':500,'message':'合同审查失败','error':str(e)}

@app.get('/contracts/{contract_id}/review')
async def get_contract_review(contract_id:int,user_id:int):
    conn=mysql()
    cursor=conn.cursor()
    cursor.execute('SELECT id,title,contract_type,status,overall_risk,review_result,review_error,reviewed_at FROM contracts WHERE id=%s AND user_id=%s',(contract_id,user_id))
    contract=cursor.fetchone()
    cursor.close()
    conn.close()
    if not contract:
        return {'code':404,'message':'合同不存在'}
    result=None
    if contract['review_result']:
        try:
            result=json.loads(contract['review_result'])
        except:
            result=contract['review_result']
    return {
        'code':200,
        'message':'查询成功',
        'contract_id':contract['id'],
        'title':contract['title'],
        'contract_type':contract['contract_type'],
        'status':contract['status'],
        'overall_risk':contract['overall_risk'],
        'reviewed_at':contract['reviewed_at'],
        'review_error':contract['review_error'],
        'data':result
    }


@app.post('/contracts/{contract_id}/dingtalk')
async def send_contract_dingtalk(contract_id:int,data:DingTalkData):
    conn=mysql()
    cursor=conn.cursor()
    cursor.execute('SELECT id,title,status,overall_risk,review_result FROM contracts WHERE id=%s AND user_id=%s',(contract_id,data.user_id))
    contract=cursor.fetchone()
    cursor.close()
    conn.close()
    if not contract:
        return {'code':404,'message':'合同不存在'}
    if contract['status']!='reviewed' or not contract['review_result']:
        return {'code':400,'message':'合同还没有完成AI审查'}
    try:
        review_result=json.loads(contract['review_result'])
        risks=review_result.get('risks',[])
        risk_text=''
        for i,item in enumerate(risks[:3]):
            risk_text=risk_text+str(i+1)+'. 【'+item.get('risk_level','')+'】'+item.get('title','')+'\n'
            risk_text=risk_text+'原因：'+item.get('reason','')+'\n\n'
        if not risk_text:
            risk_text='未发现明确风险项'
        content='''### AI合同审查人工复核提醒

**合同名称：** '''+contract['title']+'''

**综合风险：** '''+str(contract['overall_risk'])+'''

**主要风险：**

'''+risk_text+'''

**AI审查总结：**

'''+review_result.get('review_summary','')+'''

> 本结果由AI生成，仅用于辅助审查，请结合实际情况进行人工复核。
'''
        webhook=os.getenv('DINGTALK_WEBHOOK')
        response=requests.post(
            webhook,
            headers={'Content-Type':'application/json'},
            json={
                'msgtype':'markdown',
                'markdown':{
                    'title':'AI合同审查人工复核提醒',
                    'text':content
                }
            },
            timeout=10
        )
        result=response.json()
        if result.get('errcode')!=0:
            return {'code':500,'message':'钉钉发送失败','error':result}
        return {'code':200,'message':'已发送至钉钉群'}
    except Exception as e:
        return {'code':500,'message':'钉钉发送失败','error':str(e)}

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8888,
        reload=True
    )
