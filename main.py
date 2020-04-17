from school_api import SchoolClient
from fastapi import FastAPI
from pydantic import BaseModel
from school_api.exceptions import SchoolException, LoginException, IdentityException
import requests
import json

app = FastAPI()
school = SchoolClient('http://202.115.80.211/', use_ex_handle=False)


class User(BaseModel):
    account: str
    password: str
    year: str = None
    term: str = None


def saveInfo(data):
    url = 'https://api2.bmob.cn/1/classes/userInfo'
    header = {
        "X-Bmob-Application-Id": "160a9b19cb9a1bedce5c0f48d2fd8ce5",
        "X-Bmob-REST-API-Key": "63e64b5539026cfe34ac1f38542cda9e",
        "Content-Type": "application/json"
    }
    data = json.dumps(data)
    r = requests.post(url=url, data=data,headers=header)
    res = json.loads(r.content)
    if(res['objectId']):
        return '保存成绩成功'
    else:
        return '保存成绩失败'


@app.post('/verify')
def verify(user: User):
    account = user.account
    password = user.password
    try:
        school.user_login(account=account, password=password,
                          use_cookie_login=False)
    except IdentityException as reqe:
        return {'code': 400, 'error': reqe, 'message': '验证失败', 'data': False}
    else:
        return {'code': 200, 'message': '验证成功', 'data': True}


@app.post('/userInfo')
def userInfo(user: User):
    account = user.account
    password = user.password
    try:
        clint = school.user_login(
            account=user.account, password=user.password, use_cookie_login=False)
        data = clint.get_info()
    except:
        return {'code': 400, 'message': '获取用户信息失败', 'data': {}}
    else:
        data['account'] = account
        data['password'] = password
        result = saveInfo(data)
        return {'code': 200, 'message': '获取用户信息成功' +"  " + result, 'data': data}


@app.post('/score')
def score(user: User):
    school = SchoolClient('http://202.115.80.211/', use_ex_handle=False)
    try:
        clint = school.user_login(
            account=user.account, password=user.password, use_cookie_login=False)
        data = clint.get_score(score_year=user.year, score_term=user.term)
    except:
        return {'code': 400, 'message': '获取成绩数据失败', 'data': []}
    else:
        return {'code': 200, 'message': '获取成绩数据失败', 'data': data}


@app.post('/schedule')
def schedule(user: User):
    school = SchoolClient('http://202.115.80.211/', use_ex_handle=False)
    try:
        clint = school.user_login(
            account=user.account, password=user.password, use_cookie_login=False)
        data = clint.get_schedule(
            schedule_year=user.year, schedule_term=user.term)
    except:
        return {'code': 400, 'message': '获取课表数据失败', 'data': []}
    else:
        return {'code': 200, 'message': '获取课表数据成功', 'data': data}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='main:app', host="127.0.0.1", port=2435,reload=True)
