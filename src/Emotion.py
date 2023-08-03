import json
import os

import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ.get("OPEN_AI_API_KEY")

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


if __name__ == '__main__':
    for review in review_list:
        print(analyze_review(review))
