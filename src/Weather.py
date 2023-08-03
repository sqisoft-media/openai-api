import json
import os
from _datetime import datetime
from datetime import timedelta

import openai
import requests
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ.get("OPEN_AI_API_KEY")

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


def analyze(prompt , location , model="gpt-3.5-turbo-0613", temperature=0.5):
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


if __name__ == '__main__':
    current_position = get_XY("영등포의 날씨가 궁금해")
    current_weather = get_weather(current_position)
    final_analyze = analyze(current_weather , current_position["location"])
    print(final_analyze)
