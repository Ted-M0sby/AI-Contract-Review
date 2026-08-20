import os
import requests
import pymysql
from dotenv import load_dotenv

load_dotenv()

RAGFLOW_BASE_URL=os.getenv('RAGFLOW_BASE_URL')
RAGFLOW_API_KEY=os.getenv('RAGFLOW_API_KEY')
DATASET_ID='5a4db3b89bd011f18665e129ebabeb38'

def mysql():
    conn=pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='Aa123456',
        database='contract',
        port=3306,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

if __name__=="__main__":
    conn=mysql()
    cursor=conn.cursor()
    cursor.execute("SELECT id,title,cleaned_text FROM contract_corpus WHERE cleaned_text IS NOT NULL AND cleaned_text<>''")
    contracts=cursor.fetchall()

    export_dir='ragflow/contracts'
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    headers={
        'Authorization':'Bearer '+RAGFLOW_API_KEY
    }
    upload_url=RAGFLOW_BASE_URL+'/api/v1/datasets/'+DATASET_ID+'/documents'
    document_ids=[]

    for item in contracts:
        filename=str(item['id'])+'_'+item['title']+'.txt'
        file_path=os.path.join(export_dir,filename)

        with open(file_path,'w',encoding='utf-8') as f:
            f.write(item['cleaned_text'])

        with open(file_path,'rb') as f:
            files={
                'file':(filename,f,'text/plain')
            }
            response=requests.post(upload_url,headers=headers,files=files)

        print('上传：',filename,response.status_code,response.text)

        if response.status_code==200:
            data=response.json()
            if data.get('code')==0:
                for doc in data.get('data',[]):
                    document_ids.append(doc['id'])

    if document_ids:
        parse_url=RAGFLOW_BASE_URL+'/api/v1/datasets/'+DATASET_ID+'/chunks'
        response=requests.post(
            parse_url,
            headers={
                'Authorization':'Bearer '+RAGFLOW_API_KEY,
                'Content-Type':'application/json'
            },
            json={
                'document_ids':document_ids
            }
        )
        print('开始解析：',response.status_code,response.text)

    print('共处理：',len(contracts),'份合同')

    cursor.close()
    conn.close()