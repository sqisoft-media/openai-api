> ### 사전준비  
> 사용한 언어 및 라이브러리   
>언어 : Python 3.8  
>라이브러리 : openai 등 (진행하면서 import 받으면서 사용)
>
>openai api key 발급  
>https://www.daleseo.com/chatgpt-api-keys/  
>
>공공데이터 포털 오픈 API 활용 신청 및 apikey 발급  
>유물 : https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=3036708  
>날씨 : https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15084084

목차
> [1. 국립중앙박물관 유물정보 공개 API 와 openAI API 를 활용한 자연어 기반 유물 조회](#chapter-1)  
> [2. 날씨 API 연동하여 실시간 날씨를 알려주는 챗봇 기능](#chapter-2)  
> [3. 고객의 리뷰의 감정이나 내용을 판단하여 활용하는 방법](#chapter-3)

##### 1. 국립중앙박물관 유물정보 공개 API 와 openAI API 를 활용한 자연어 기반 유물 조회<a id="chapter-1"></a>

간단한 검색기능을 구현하기 위해 공공 API 에서 쓸만한 데이터를 찾아보았습니다   
공공 데이터 포털의 문화체육관광부 국립중앙박물관_전국 박물관 유물정보 API 를 활용했습니다
https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=3036708#tab_layer_detail_function

일단 프로젝트 최상단에 .env파일을 생성 후 api key를 세팅합니다

```dotenv
OPEN_AI_API_KEY = apikey
MUSEUM_API_KEY = 공공데이터 apikey
```

먼저 유물정보를 요청하는 python 함수입니다

```python
import os
import requests
import xml.etree.ElementTree as elemTree
from dotenv import load_dotenv

load_dotenv()


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
```

요청을 보낼때

- 크기범위
- 용도/기능분류
- 재질
- 국적
- 출토지

위 데이터를 가변적으로 넣어 검색 기능을 할 수 있게 만들고

응답을 받을때는 
- 박물관 이름 
- 유물이름 
- 이미지 url  

을 가져옵니다 

이후 요청을 보낼때 사용할 코드를 정의하기 위해 API 문서를 참고하여 json 으로 저장해줍니다.  
```python
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
    "materialCode": [
        {'name': '기타', 'code': 'PS08099'}, {'name': '칠기', 'code': 'PS08017'}, {'name': '합성재질', 'code': 'PS08016'},
        {'name': '고무', 'code': 'PS08015'}, {'name': '화석', 'code': 'PS08014'}, {'name': '광물', 'code': 'PS08013'},
        {'name': '씨앗', 'code': 'PS08012'}, {'name': '섬유', 'code': 'PS08011'}, {'name': '가죽/털', 'code': 'PS08010'},
        {'name': '종이', 'code': 'PS08009'}, {'name': '뼈/뿔/조개', 'code': 'PS08008'}, {'name': '나무', 'code': 'PS08007'},
        {'name': '풀', 'code': 'PS08006'}, {'name': '유리/보석', 'code': 'PS08005'}, {'name': '돌', 'code': 'PS08004'},
        {'name': '도자기', 'code': 'PS08003'}, {'name': '흙', 'code': 'PS08002'}, {'name': '금속', 'code': 'PS08001'}]
    ,
    # 국적
    "nationalityCode": [
        {'name': '기타', 'code': 'PS06090'}, {'name': '오세아니아', 'code': 'PS06009'}, {'name': '아메리카', 'code': 'PS06008'},
        {'name': '유럽', 'code': 'PS06007'}, {'name': '아프리카', 'code': 'PS06006'}, {'name': '중동', 'code': 'PS06005'},
        {'name': '아시아', 'code': 'PS06004'}, {'name': '일본', 'code': 'PS06003'}, {'name': '중국', 'code': 'PS06002'},
        {'name': '한국', 'code': 'PS06001'}],
    # 출토지
    "placeLandCode": [{'name': '세종특별자치시', 'code': 'GL05017'}, {'name': '울산광역시', 'code': 'GL05016'}, {'name': '충청북도', 'code': 'GL05015'},
                      {'name': '충청남도', 'code': 'GL05014'}, {'name': '제주도', 'code': 'GL05013'}, {'name': '전라북도', 'code': 'GL05012'},
                      {'name': '전라남도', 'code': 'GL05011'}, {'name': '경상북도', 'code': 'GL05010'}, {'name': '경상남도', 'code': 'GL05009'},
                      {'name': '경기도', 'code': 'GL05008'}, {'name': '강원도', 'code': 'GL05007'}, {'name': '대전광역시', 'code': 'GL05006'},
                      {'name': '광주광역시', 'code': 'GL05005'}, {'name': '인천광역시', 'code': 'GL05004'}, {'name': '대구광역시', 'code': 'GL05003'},
                      {'name': '부산광역시', 'code': 'GL05002'}, {'name': '서울특별시', 'code': 'GL05001'}]
}
```

이렇게 구성하게 되면 각 목적에 따라 필요한 데이터를 코드별로 검색하여 가져올 수 있습니다

```python
# 국적 검색
if __name__ == '__main__':
    # 국적에 따른 검색
    get_relic(nationalityCode=codeList['nationalityCode'][0]['code'])
    # 재질에 따른 검색
    get_relic(materialCode=codeList['materialCode'][0]['code'])
    # 출토지에 따른 검색
    get_relic(placeLandCode=codeList['placeLandCode'][0]['code'])
    # 용도/기능분류에 따른 검색
    get_relic(purposeCode=codeList['purposeCode'][0]['code'])
    # 용도/기능분류와 재질 코드에 따른 검색
    get_relic(purposeCode=codeList['purposeCode'][0]['code'], materialCode=codeList['materialCode'][0]['code'])[0]['code'])
```

이제 ChatGPT openAI API 와 연동하는 작업을 하겠습니다

앞서 본격적인 연동 전 openAI API 를 기본적으로 연동하는 방법입니다  
이 API 를 사용하는건 웹에서 ChatGPT 를 사용하는 것과 같은 역할을 합니다

```python
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.environ.get("OPEN_AI_API_KEY")


def simple_get_completion(messages, model="gpt-3.5-turbo-0613", temperature=0):
    messages = [
        {"role": "user", "content": messages}
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message["content"]


if __name__ == '__main__':
    result = simple_get_completion("python 으로 helloworld 를 보여주는 코드를 짜줘")
    print(result)

```

이후 아래와 같은 응답을 받을 수 있습니다
>
>아래는 Python 으로 HelloWorld 를 출력하는 코드입니다:
>
>```python
> print("Hello, World!")
>```
>
>이 코드를 실행하면 "Hello, World!"라는 메시지가 출력됩니다.

이제 본격적인 연동 작업을 하겠습니다  
연동 전 저희가 만든 함수를 연동하기 위해서 가장 먼저 chatGPT 에게 저희가 만든 get_relic 함수를 설명해줘야 합니다

```python
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
```

위와 같이 functions 에 chatGPT 가 호출하고자 하는 함수를 설명해주면 됩니다  

이를 functions calling 방식 이라고 부릅니다 나온지 오래 되지않은 기능이라 최신 gpt 모델(gpt-3.5-turbo-0613) 에서만 사용이 가능합니다  
참고 : https://platform.openai.com/docs/guides/gpt/function-calling  

이렇게 함수에 대해 chatGPT 에게 설명을 해주고 나면 채팅 내용에서 유물관련 검색이 필요하다고 판단되었을때       
chatGPT 가 get_relic() 함수를 자동으로 호출 해줍니다

openAI API 호출하는 최종 코드입니다

```python
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
```

유물을 찾는경우(함수가 필요하다고 생각되는 경우)를 chatGPT 가 알아서 판단 후 get_relic() 함수를 호출 해줍니다

이제 아래와 같이 자연어 기반 검색 기능이 사용 가능합니다  
유물을 자세하게 찾아야 되는 직업군(큐레이터)의 사용자에게 유용하게 사용될 수 있을 것 같습니다.

```python
if __name__ == '__main__':
    # 저희가 만든 get_relic()함수를 호출합니다
    # {'sizeRangeCode': 'PS15002', 'purposeCode': 'PS09008', 'materialCode': 'PS08001', 'nationalityCode': 'GL05008'}
    # chatGPT가 손가락 한마디라는 자연어를 해석해서 5~10cm라는 조건을 넣어줍니다 
    print(get_completion("유물을 하나 찾고있어 경기도에서 발견된 유물인데  손가락 한마디 정도 되는 것 같고 종교랑 관련있고 철로 된 유물이야 어떤건지 알아봐줘?"))

    # {'nationalityCode': 'PS06003', 'purposeCode': 'PS09008'}
    print(get_completion("일본의 종교문화와 관련된 유물을 보여줘"))

    # get_relic()함수가 아니라 기본 챗봇 기능을 활용합니다 
    print(get_completion("chatGPT를 잘 활용하는 방법을 알려줘"))

```

이를 이용해 자연어를 기반으로 유물을 찾는 기능을 만들어보았습니다  
현재는 간단하게 공공 API 를 이용하는 방법만 사용했지만 저희 서비스의 DB 를 대상으로 검색엔진을 구축하고 이를 이용해 저희 서비스에 chatGPT 를 적용할 수 있을 것 같습니다.

##### 2. 날씨 API 연동하여 실시간 날씨를 알려주는 챗봇 기능<a id="chapter-2"></a>

https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15084084

이전에 사용한 .env 파일의 MUSEUM_API_KEY 을 공통적으로 사용하기 때문에 따로 설정할 필요가 없습니다

먼저 날씨 API 를 호출하는 함수를 만들어줍니다

```python
def get_weather(xy):
    target_date = datetime.now() - timedelta(hours=1)
    params = {
        "ServiceKey": os.environ.get("MUSEUM_API_KEY"),
        "pageNo": 1,
        "numOfRows": 1000,
        "dataType": "json",
        "base_date": target_date.strftime("%Y%m%d"),
        "base_time": target_date.strftime("%H%M"),
        "nx": xy["x"],
        "ny": xy["y"],
    }
    response = requests.get("http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst", params)
    if response.status_code == 200:
        return json.loads(response.text)["response"]["body"]["items"]["item"]
    else:
        print("요청 실패")
```

위 함수는 X,Y 좌표를 받으면 그 날씨 데이터를 JSON 으로 return 하는 함수입니다

여기서 X,Y 좌표는 API 제공하는 측에서 파일로 제공해줍니다 약 4천개의 데이터가 있는데 너무 양이 많아 토큰이 부족하기 때문에 일단 서울 데이터만 가져오겠습니다   
참고로 토큰의 제한은 4k(gpt-3.5-turbo)인데 최근에 16k(gpt-3.5-turbo-16k)까지 사용가능한 모델이 나와서   
참고 : https://platform.openai.com/docs/models/gpt-3-5  
아래와 같은 데이터를 넣으면 약 2000개 정도는 가능합니다

```python
xyInfo = """
1단계,2단계,격자 X,격자 Y
서울특별시,,60,127
서울특별시,종로구,60,127
서울특별시,중구,60,127
서울특별시,용산구,60,126
서울특별시,성동구,61,127
서울특별시,광진구,62,126
서울특별시,동대문구,61,127
서울특별시,중랑구,62,128
서울특별시,성북구,61,127
서울특별시,강북구,61,128
서울특별시,도봉구,61,129
서울특별시,노원구,61,129
서울특별시,은평구,59,127
서울특별시,서대문구,59,127
서울특별시,마포구,59,127
서울특별시,양천구,58,126
서울특별시,강서구,58,126
서울특별시,구로구,58,125
서울특별시,금천구,59,124
서울특별시,영등포구,58,126
서울특별시,동작구,59,125
서울특별시,관악구,59,125
서울특별시,서초구,61,125
서울특별시,강남구,61,126
서울특별시,송파구,62,126
서울특별시,강동구,62,126
"""
```

여기서 X,Y좌표를 뽑아낼때 chatGPT를 사용해보겠습니다

```python
def get_XY(location, model="gpt-3.5-turbo-0613", temperature=0):
    messages = [
        {"role": "system", "content": f"""
        '''로 감싸져있는 CSV 에서 내가 물어보는 지역의 X,Y 좌표를 찾아서 반환해줘 '구' 라는 글자가 생략되거나 '특별시' 라는 글자가 생략될수도 있어
        '''
        {xyInfo}
        '''
        응답은 json 으로 해줘 e.g. {{"location" : 내가 물어본 위치 e.g. 서울특별시 영등포구 , "x": x, "y": y}}
        """
         },
        {"role": "user", "content": location}
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    message = response.choices[0].message
    return json.loads(message["content"])
```

위 함수는 저희가 만든 xyInfo라는 변수를 가져와서 영등포 , 서울 , 양천 이런식으로 데이터를 넣으면 X,Y 좌표를 json으로 반환해주는 함수입니다

이제 실시간 날씨를 가져오기위해 위 함수들을 호출해보겠습니다

```python
if __name__ == '__main__':
    current_position = get_XY("영등포의 날씨가 궁금해")
    current_weather = get_weather(current_position)
```

이렇게 호출하게 되면 current_weather 에는 유저가 원하는 지역의 현재 실시간 날씨관련 데이터가 들어가게 됩니다

```json
[
  {
    'baseDate': '20230625',
    'baseTime': '1400',
    'category': 'PTY',
    'nx': 58,
    'ny': 126,
    'obsrValue': '0'
  },
  {
    'baseDate': '20230625',
    'baseTime': '1400',
    'category': 'REH',
    'nx': 58,
    'ny': 126,
    'obsrValue': '44'
  },
  {
    'baseDate': '20230625',
    'baseTime': '1400',
    'category': 'RN1',
    'nx': 58,
    'ny': 126,
    'obsrValue': '0'
  },
  {
    'baseDate': '20230625',
    'baseTime': '1400',
    'category': 'T1H',
    'nx': 58,
    'ny': 126,
    'obsrValue': '32.4'
  },
  {
    'baseDate': '20230625',
    'baseTime': '1400',
    'category': 'UUU',
    'nx': 58,
    'ny': 126,
    'obsrValue': '-1.6'
  },
  {
    'baseDate': '20230625',
    'baseTime': '1400',
    'category': 'VEC',
    'nx': 58,
    'ny': 126,
    'obsrValue': '93'
  },
  {
    'baseDate': '20230625',
    'baseTime': '1400',
    'category': 'VVV',
    'nx': 58,
    'ny': 126,
    'obsrValue': '0.1'
  },
  {
    'baseDate': '20230625',
    'baseTime': '1400',
    'category': 'WSD',
    'nx': 58,
    'ny': 126,
    'obsrValue': '1.7'
  }
]
```

이제 이상태로 사용자에게 보여주기보다는 이를 설명하는 chatGPT 함수를 만들어서 좀 더 보기좋게 바꿔보겠습니다

```python
def analyze(prompt, location, model="gpt-3.5-turbo-0613", temperature=0.5):
    messages = [
        {"role": "system", "content": f"""
            내가 물어보는 json 데이터를 분석해서 한글로 설명해줘 각 요소의 데이터는 아래와 같아 \n\n
            
            T1H : 현재 기온이야,단위는 ℃
            RN1 : 강수량이야 0mm 이거나 그 근처이면 비가 안온다고 설명해줘 ,단위는 mm
            UUU : 동쪽에서 서쪽으로 부는 바람의 속도야 높지 않으면 굳이 설명하지 않아도 돼,단위는 m/s
            VVV : 남쪽에서 북쪽으로 부는 바람의 속도야 높지 않으면 굳이 설명하지 않아도 돼,단위는 m/s
            REH : 습도야 습도가 높으면 불쾌지수가 높으니까 여기에 대해 설명해주면 좋을 것 같아,단위는 % 
            PTY : 강수야 각 값에대한 내용은 다음과 같아 0일때는 설명하지 않고 다른경우에는 강조해야돼 0:없음, 1:비, 2:비 또는 눈, 3:눈, 5:빗방울, 6:빗방울눈날림, 7:눈날림 
            VEC : 풍향 , 단위는 deg (0~360) 0~90 동풍, 90~180 남풍, 180~270 서풍, 270~360 북풍
            WSD : 풍속이야 높은 경우 강조해야돼, 단위는 m/s 
            
            마지막으로 현재 위치는 {location}이야 너의 설명에 꼭 포함되어야해
        """},
        {"role": "user", "content": json.dumps(prompt)}
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    print(response.get("usage").get("total_tokens"))
    message = response.choices[0].message
    return message["content"]
```

위와같이 구성하게 되면 날씨를 설명해주는 chatGPT 함수를 만들 수 있습니다.

> 현재 서울특별시 영등포구의 기상 데이터입니다.
>
>- 현재 기온은 32.4℃입니다.
>- 강수량은 0mm이며, 비가 오지 않습니다.
>- 동쪽에서 서쪽으로 바람이 1.6m/s로 부는 것으로 나타났습니다.
>- 남쪽에서 북쪽으로 바람이 0.1m/s로 부는 것으로 나타났습니다.
>- 습도는 44%로, 불쾌지수에 영향을 줄만큼 높은 수치는 아닙니다.
>- 강수는 없으며, PTY 값이 0이므로 강수에 대한 설명은 필요하지 않습니다.
>- 바람의 풍향은 93도로 북풍입니다.
>- 풍속은 1.7m/s로, 비교적 낮은 수치입니다.

위와 같이 데이터가나오는데 너무 딱딱해보이고 'PTY 값이 0이므로 강수에 대한 설명은 필요하지 않습니다' 와 같은 쓸데없는 데이터가 들어가게 됩니다

여기서 chatGPT 를 활용하는 방법중 역할부여를 사용해보겠습니다  
참고로 chatGPT 를 잘 활용하는방법은 https://platform.openai.com/docs/guides/gpt-best-practices 여기 잘정리되어있습니다  
그 중 Ask the model to adopt a persona 방법을 활용해보겠습니다

```python
def analyze(prompt, location, model="gpt-3.5-turbo-0613", temperature=0.5):
    messages = [
        {"role": "system", "content": f"""
            너의 역할은 기상캐스터야 너에게 원하는 조건은 아래와 같아 \n\n
            1. 너는 현재 기온 , 강수량 , 습도 그리고 강수 형태에 대해 상세하게 설명해주는 사람이야
            2. 바람성분이나 풍향에 대해서는 특별한 경우에만 설명해줘
            3. 너무 딱딱한 말투가 아니라 자유로운 분위기로 설명해줘
            4. 날씨만 설명하지 않고 그 날씨에 대해 너의 생각도 같이 달아줘
            5. 현재 날씨를 기준으로 사람이 느낄만한 감정을 알려줘 (불쾌지수가 높다거나 상쾌한 날씨라거나)
            6. 남녀노소 누구나 이해할 수 있게 쉽게 설명해줘. 존댓말로 해야돼.
            
            내가 물어보는 json 데이터를 분석해서 한글로 설명해줘 각 요소의 데이터는 아래와 같아 \n\n
            
            T1H : 현재 기온이야,단위는 ℃
            RN1 : 강수량이야 0mm 이거나 그 근처이면 비가 안온다고 설명해줘 ,단위는 mm
            UUU : 동쪽에서 서쪽으로 부는 바람의 속도야 높지 않으면 굳이 설명하지 않아도 돼,단위는 m/s
            VVV : 남쪽에서 북쪽으로 부는 바람의 속도야 높지 않으면 굳이 설명하지 않아도 돼,단위는 m/s
            REH : 습도야 습도가 높으면 불쾌지수가 높으니까 여기에 대해 설명해주면 좋을 것 같아,단위는 % 
            PTY : 강수야 각 값에대한 내용은 다음과 같아 0일때는 설명하지 않고 다른경우에는 강조해야돼 0:없음, 1:비, 2:비 또는 눈, 3:눈, 5:빗방울, 6:빗방울눈날림, 7:눈날림 
            VEC : 풍향 , 단위는 deg (0~360) 0~90 동풍, 90~180 남풍, 180~270 서풍, 270~360 북풍
            WSD : 풍속이야 높은 경우 강조해야돼, 단위는 m/s 
            
            마지막으로 현재 위치는 {location}이야 너의 설명에 꼭 포함되어야해
        """},
        {"role": "user", "content": json.dumps(prompt)}
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    print(response.get("usage").get("total_tokens"))
    message = response.choices[0].message
    return message["content"]
```

참고로 temperature 의 경우 0에서 까지의 값을 넣을 수 있는데 0의경우 호출할때마다 응답의 내용이나 형식이 같은 형식으로 나오고    
1에 가까워질 수록 호출할때마다 글의 내용이나 형식이 다양하게 나옵니다.

여기서 추가된 내용은 아래와 같습니다

> 너의 역할은 기상캐스터야 너에게 원하는 조건은 아래와 같아
>1. 너는 현재 기온 , 강수량 , 습도 그리고 강수 형태에 대해 상세하게 설명해주는 사람이야
>2. 바람성분이나 풍향에 대해서는 특별한 경우에만 설명해줘
>3. 너무 딱딱한 말투가 아니라 자유로운 분위기로 설명해줘
>4. 날씨만 설명하지 않고 그 날씨에 대해 너의 생각도 같이 달아줘
>5. 현재 날씨를 기준으로 사람이 느낄만한 감정을 알려줘 (불쾌지수가 높다거나 상쾌한 날씨라거나)
>6. 남녀노소 누구나 이해할 수 있게 쉽게 설명해줘. 존댓말로 해야돼.

```python
if __name__ == '__main__':
    current_position = get_XY("영등포의 날씨가 궁금해")
    current_weather = get_weather(current_position)
    final_analyze = analyze(current_weather, current_position["location"])
    print(final_analyze)
```

이후 다시 호출해보면 다음과같은 결과가 나옵니다
> 현재 서울특별시 영등포구의 기상 상황을 알려드릴게요.
>
>현재 기온은 32.6도로 높은 편이에요. 날씨가 더워지고 있으니 불쾌할 수 있으니 조금 더위에 주의해주세요.
>
>강수량은 0mm이에요. 비가 오지 않아서 다행이네요.
>
>습도는 44%로 적당한 수준이에요. 습도가 낮아서 상쾌한 느낌이겠죠.
>
>바람은 동쪽에서 서쪽으로 약간 부는 풍향이에요. 바람의 속도는 1.7m/s로 약하니 크게 느껴지지 않을거에요.
>
>그리고 강수 형태는 없으니 우산을 챙기지 않아도 돼요.
>
>오늘 서울특별시 영등포구의 날씨는 더워서 불쾌할 수 있으니 조금 더위에 주의해주세요. 비가 오지 않아서 다행이에요. 바람도 약하게 부는 편이니 시원한 바람을 느낄 수 있을거에요.
>
>더 자세한 정보가 필요하시면 언제든지 물어보세요!

아직 부족해보이지만 이정도면 충분히 쓸만한 결과가 나온것 같습니다.  

##### 3. 고객 리뷰의 감정이나 내용을 판단하여 활용하는 방법<a id="chapter-3"></a>

마지막으로 간단하게 chatGPT 를 활용하는 방법입니다 다들 아시다시피 chatGPT 같은 대화기반 인공지능 모델은 감정이나 내용을 판단하는데 활용하기 좋습니다

```python
review_list = [
    "디자인이 제 스타일과는 맞지 않아서 좀 아쉬웠어요. 다른 디자인으로 교환하려고 생각 중입니다.",
    "제가 원하는 스타일에 딱 맞는 제품이었어요. 색상도 예쁘고 크기도 딱 좋았어요. 사용하기 편해서 정말 만족합니다.",
    "색상이 사진과 너무 다르게 나와서 좀 화가 났어요. 설명에 써 있는 것과 전혀 다른 색감이라서 짜증이 났어요.",
    "색상이 사진과 많이 다르게 나와서 조금 실망했어요. 설명에 써 있는 것과 다른 색감이라서 좀 당황스러웠어요.",
    "물건을 받자마자 느낀 건 '와, 진짜 고급스러워!' 퀄리티가 정말 좋고, 디자인도 세련되어 보였어요. 정말 훌륭한 제품이에요!",
    "크기가 제 예상과 맞지 않아서 사용하기가 불편했어요. 너무 작아서 제대로 사용할 수 없어서 화가 났어요.",
    "구매한 이후로 계속 이 물건을 사람들에게 추천하고 다니는 중이에요. 정말 신뢰할 만한 브랜드고, 제품의 퀄리티와 성능이 일류입니다.",
    "배송이 아직도 안오는데 어떻게 환불하는 방법이 없나요? 전화도 안받고, 메일도 안읽어주고, 정말 답답하네요.",
    "이 물건은 정말 훌륭해요! 품질도 좋고 디자인도 멋있어서 마음에 들었어요. 사진과 실물이 딱 맞아서 기대 이상이었어요.",
    "퀄리티가 기대보다 낮아서 실망했어요. 사용 중에도 계속 문제가 생기고, 내구성이 좋지 않아서 좀 아쉬웠어요.",
    "배송이 예상보다 늦어져서 좀 답답했어요. 상품 자체는 괜찮았는데, 배송 서비스가 좀 아쉬웠어요.",
    "크기가 제 예상과 맞지 않아서 사용하기가 불편했어요. 조금 더 크거나 작았으면 좋겠다고 생각했어요.",
    "퀄리티가 기대보다 낮아서 정말 실망했어요. 사용 중에도 계속 문제가 생기고, 내구성이 좋지 않아서 정말 속상하네요.",
    "배송도 빠르고 포장도 꼼꼼히 해줘서 좋았어요. 물건을 받았을 때 기분이 정말 좋았고, 사용해보니 정말 편하고 실용적이에요.",
]
```

다음과 같은 리뷰 리스트를 가져왔습니다 chatGPT 로 생성한 결과물입니다 이후 다음과같은 프롬프트를 사용하여 리뷰를 분석해보겠습니다

```python
def analyze_review(prompt, model="gpt-3.5-turbo-0613", temperature=0):
    messages = [
        {"role": "system", "content": """ 
        지금부터 내가 물어보는 내용은 고객의 리뷰야
        여기서 다양한 정보를 추출해서 알려줘
        응답은 json 으로 해줘 
        내가 원하는 json 응답은 아래와 같아 /n/n
        {
        "positive" : 이 리뷰가 긍정적인 리뷰인지 부정적인 리뷰인지 알려줘 응답은 True or False 로 해줘 e.g. "positive" : True
            "anger" : 고객이 화가 났는지 알려줘 응답은 True or False 로 해줘 e.g. "anger" : True
            "refund" : 고객이 환불을 고려중인지 확인해보고 그 언급한 내용을 리스트로 알려줘 e.g. "refund" : ["환불", "환불해줘"],
            "price": 고객이 가격에 대해 언급을 했으면 그 언급한 내용을 리스트로 알려줘 e.g. "price" : ["비싸다", "싼", "적당하다"]
            "delivery": 고객이 택배 시간에 대해 언급을 했으면 그 언급한 내용을 리스트로 알려줘 e.g. "delivery" : ["느리다", "빠르다"]
            "value" :고객이 이 물건의 가치에 대해 언급을 했으면 그 언급한 내용을 리스트로 알려줘 e.g. "value" : ["가치", "가치가 있다", "가치가 없다"]
        }
        """
         },
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    message = response.choices[0].message
    return json.loads(message["content"])
```

이후 아래의 코드를 실행시키면 나오는 결과입니다
```python
if __name__ == '__main__':
    for review in review_list:
        print(analyze_review(review))
```
> {'positive': False, 'anger': False, 'refund': [], 'price': [], 'delivery': [], 'value': []}  
{'positive': True, 'anger': False, 'refund': [], 'price': [], 'delivery': [], 'value': []}  
{'positive': False, 'anger': True, 'refund': [], 'price': [], 'delivery': [], 'value': []}  
{'positive': False, 'anger': False, 'refund': [], 'price': [], 'delivery': [], 'value': []}  
{'positive': True, 'anger': False, 'refund': [], 'price': [], 'delivery': [], 'value': []}  
{'positive': False, 'anger': True, 'refund': [], 'price': [], 'delivery': [], 'value': []}  
{'positive': True, 'anger': False, 'refund': [], 'price': [], 'delivery': [], 'value': []}  
{'positive': False, 'anger': True, 'refund': ['환불', '환불하는 방법'], 'price': [], 'delivery': ['배송', '안오는', '답답'], 'value': []} {'positive': True, 'anger': False, 'refund': [], 'price': [], 'delivery': [], 'value': []}  
{'positive': False, 'anger': False, 'refund': [], 'price': [], 'delivery': [], 'value': ['퀄리티가 낮다', '실망']}  
{'positive': True, 'anger': False, 'refund': [], 'price': [], 'delivery': ['느리다'], 'value': []}  
{'positive': False, 'anger': False, 'refund': [], 'price': [], 'delivery': [], 'value': []}  
{'positive': False, 'anger': False, 'refund': [], 'price': [], 'delivery': [], 'value': ['퀄리티가 낮다', '실망', '문제가 생기다', '내구성이 좋지 않다', '속상하다']}  
{'positive': True, 'anger': False, 'refund': [], 'price': [], 'delivery': ['빠르다'], 'value': ['편하다', '실용적이다']}  

이를 활용하여 많은 리뷰를 전부 읽고 , 분석 할 필요 없이 고객이 화난 것 같으면 빠른 대응을 할 수 있고, 전체적인 리뷰의 빠른 분석이 가능하게 됩니다  