import os
import xml.etree.ElementTree as elemTree

import openai
import requests
import json
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ.get("OPEN_AI_API_KEY")

codeList = {
    # 크기 범위
    'sizeRangeCode': [{'name': '20 m 이상', 'code': 'PS15011'}, {'name': '15~20 m', 'code': 'PS15010'},
                      {'name': '10~15 m', 'code': 'PS15009'}, {'name': '5~10 m', 'code': 'PS15008'}, {'name': '1~5 m', 'code': 'PS15007'},
                      {'name': '70~100 cm', 'code': 'PS15006'}, {'name': '50~70 cm', 'code': 'PS15005'},
                      {'name': '30~50 cm', 'code': 'PS15004'}, {'name': '10~30 cm', 'code': 'PS15003'},
                      {'name': '5~10 cm', 'code': 'PS15002'}, {'name': '5 cm 이하', 'code': 'PS15001'}],
    # 용도/기능분류
    "purposeCode": [{'name': '기타자료', 'code': 'PS09099'}, {'name': '미디어', 'code': 'PS09013'},
                    {'name': '과학기술', 'code': 'PS09012'},
                    {'name': '보건의료', 'code': 'PS09011'}, {'name': '군사', 'code': 'PS09010'},
                    {'name': '문화예술', 'code': 'PS09009'},
                    {'name': '종교신앙', 'code': 'PS09008'}, {'name': '사회생활', 'code': 'PS09007'},
                    {'name': '전통과학', 'code': 'PS09006'},
                    {'name': '교통/통신', 'code': 'PS09005'}, {'name': '산업/생업', 'code': 'PS09004'},
                    {'name': '주생활', 'code': 'PS09003'},
                    {'name': '식생활', 'code': 'PS09002'}, {'name': '의생활', 'code': 'PS09001'}],
    # 재질
    "materialCode":
        [{'name': '기타', 'code': 'PS08099'}, {'name': '칠기', 'code': 'PS08017'}, {'name': '합성재질', 'code': 'PS08016'},
         {'name': '고무', 'code': 'PS08015'}, {'name': '화석', 'code': 'PS08014'}, {'name': '광물', 'code': 'PS08013'},
         {'name': '씨앗', 'code': 'PS08012'}, {'name': '섬유', 'code': 'PS08011'}, {'name': '가죽/털', 'code': 'PS08010'},
         {'name': '종이', 'code': 'PS08009'}, {'name': '뼈/뿔/조개', 'code': 'PS08008'}, {'name': '나무', 'code': 'PS08007'},
         {'name': '풀', 'code': 'PS08006'}, {'name': '유리/보석', 'code': 'PS08005'}, {'name': '돌', 'code': 'PS08004'},
         {'name': '도자기', 'code': 'PS08003'}, {'name': '흙', 'code': 'PS08002'}, {'name': '금속', 'code': 'PS08001'}]
    ,
    # 국적
    "nationalityCode":
        [{'name': '기타', 'code': 'PS06090'}, {'name': '오세아니아', 'code': 'PS06009'}, {'name': '아메리카', 'code': 'PS06008'},
         {'name': '유럽', 'code': 'PS06007'}, {'name': '아프리카', 'code': 'PS06006'}, {'name': '중동', 'code': 'PS06005'},
         {'name': '아시아', 'code': 'PS06004'}, {'name': '일본', 'code': 'PS06003'}, {'name': '중국', 'code': 'PS06002'},
         {'name': '한국', 'code': 'PS06001'}]
    ,
    # 출토지
    "placeLandCode": [{'name': '세종특별자치시', 'code': 'GL05017'}, {'name': '울산광역시', 'code': 'GL05016'}, {'name': '충청북도', 'code': 'GL05015'},
                      {'name': '충청남도', 'code': 'GL05014'}, {'name': '제주도', 'code': 'GL05013'}, {'name': '전라북도', 'code': 'GL05012'},
                      {'name': '전라남도', 'code': 'GL05011'}, {'name': '경상북도', 'code': 'GL05010'}, {'name': '경상남도', 'code': 'GL05009'},
                      {'name': '경기도', 'code': 'GL05008'}, {'name': '강원도', 'code': 'GL05007'}, {'name': '대전광역시', 'code': 'GL05006'},
                      {'name': '광주광역시', 'code': 'GL05005'}, {'name': '인천광역시', 'code': 'GL05004'}, {'name': '대구광역시', 'code': 'GL05003'},
                      {'name': '부산광역시', 'code': 'GL05002'}, {'name': '서울특별시', 'code': 'GL05001'}]
}


def get_completion(messages, model="gpt-3.5-turbo-0613", temperature=0):
    functions = [
        {
            "name": "get_relic",
            "description": "사용자가 원하는 유물을 다양한 조건으로 찾아주는 함수",
            "parameters": {
                "type": "object",
                "properties": {
                    "sizeRangeCode": {
                        "type": "string",
                        "description": f"""아래의 json 에서 name 과 관련된 코드를 선택해줘 \n\n e.g. PS15010 {codeList["sizeRangeCode"]}""",
                    },
                    "purposeCode": {
                        "type": "string",
                        "description": f"""아래의 json 에서 name 과 관련된 코드를 선택해줘 \n\n e.g. PS15010 {codeList["purposeCode"]}""",
                    },
                    "materialCode": {
                        "type": "string",
                        "description": f"""아래의 json 에서 name 과 관련된 코드를 선택해줘 \n\n e.g. PS15010 {codeList["materialCode"]}""",
                    },
                    "nationalityCode": {
                        "type": "string",
                        "description": f"""아래의 json 에서 name 과 관련된 코드를 선택해줘 \n\n e.g. PS15010 {codeList["nationalityCode"]}""",
                    },
                    "placeLandCode": {
                        "type": "string",
                        "description": f"""아래의 json 에서 name 과 관련된 코드를 선택해줘 \n\n e.g. PS15010 {codeList["placeLandCode"]}""",
                    }
                },
                # 반드시 받아야되는 파라미터가 있으면 여기에 입력
                "required": [],
            },
        }
    ]
    messages = [
        {"role": "user", "content": messages}
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        functions=functions,
        temperature=temperature,
    )
    message = response.choices[0].message
    if message.get("function_call") is not None:
        # chatGPT 가 함수를 호출하기로 판단했을때 여기로 옵니다
        available_functions = {
            "get_relic": get_relic,
        }
        target_function = message["function_call"]["name"]
        target_parameter = json.loads(message["function_call"].get("arguments"))
        # 이 response 데이터를 이용해서 웹이나 앱에 띄워주기
        response = available_functions[target_function](
            sizeRangeCode=target_parameter.get("sizeRangeCode"),
            purposeCode=target_parameter.get("purposeCode"),
            materialCode=target_parameter.get("materialCode"),
            nationalityCode=target_parameter.get("nationalityCode"),
            placeLandCode=target_parameter.get("placeLandCode")
        )
        return response
    else:
        # chatGPT 가 함수를 호출하지 않아도 된다고 판단했을때 여기로 옵니다
        return message["content"]


def get_relic(pageNo=1,
              numOfRows=10,
              sizeRangeCode=None,
              purposeCode=None,
              materialCode=None,
              nationalityCode=None,
              placeLandCode=None):
    # param
    params = {
        "serviceKey": os.environ.get("MUSEUM_API_KEY"),
        "pageNo": pageNo,
        "numOfRows": numOfRows,
    }
    if sizeRangeCode is not None:
        params["sizeRangeCode"] = sizeRangeCode
    if purposeCode is not None:
        params["purposeCode"] = purposeCode
    if materialCode is not None:
        params["materialCode"] = materialCode
    if nationalityCode is not None:
        params["nationalityCode"] = nationalityCode
    if placeLandCode is not None:
        params["placeLandCode"] = placeLandCode

    # 요청 보내기
    response = requests.get("http://www.emuseum.go.kr/openapi/relic/list", params=params)

    if response.status_code == 200:
        # 요청 성공시 XML 파싱후 dictionary list 로 변경
        return list(map(
            lambda element: {
                "museumNm": element.find('.//item[@key="museumName2"]').get('value'),
                "relicNm": element.find('.//item[@key="name"]').get('value'),
                "imageUrl": element.find('.//item[@key="imgThumUriL"]').get('value').replace("211.252.141.59", "http://www.emuseum.go.kr")
            },
            elemTree.fromstring(response.text).findall('.//list/data')
        ))
    else:
        print("요청 실패")


if __name__ == '__main__':
    # 저희가 만든 get_relic 을 호출합니다
    # {'sizeRangeCode': 'PS15003', 'purposeCode': 'PS09008', 'materialCode': 'PS08001', 'nationalityCode': 'GL05008'}
    print(get_completion("유물을 하나 찾고있어 경기도에서 발견된 유물인데 손가락 한마디 정도 되는 것 같고 종교랑 관련있고 철로 된 유물이야 어떤건지 알아봐줘?"))

    # {'nationalityCode': 'PS06003', 'purposeCode': 'PS09008'}
    print(get_completion("일본의 종교문화와 관련된 유물을 보여줘"))

    # 유물에 관련된 내용이 아니라 기본 챗봇 기능을 활용합니다
    print(get_completion("chatGPT 를 잘 활용하는 방법을 알려줘"))
