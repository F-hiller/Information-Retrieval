정보검색 과제
                     경북대학교 컴퓨터학부 
2020114732 최준호   

0.      목차
1.	개요
2.	프로그램 설명
3.	관련 자료
4.	실행 결과

1. 개요

정보검색에서 배운 내용들을 활용하여 corpus에서 쿼리를 원하는 문서를 검색하는 것이 목표이다. 가장 원하는 문서에 가깝다고 생각하는 5개를 골라서 화면에 출력해야한다.

언어는 python을 사용하였으며 해당 프로그램에 사용된 방식은 다음과 같이 나타낼 수 있습니다.
1) 사전 api를 통한 단어의 normalizing
2) normalizing된 단어들을 이용하여 tf-idf 계산
3) 입력된 쿼리 또한 normalizing
4) 쿼리가 포함된 문서들의 tf-idf 가중치 값을 바탕으로 점수 계산
5) 결과 출력

2. 프로그램 설명

1) 사전 api를 통한 단어의 normalizing

국어사전에 어떠한 단어/문장을 검색하면 가장 유사도가 높은 단어들을 알려줍니다. 즉, “대통령”과 “대통령에게” 모두 국어사전을 거치면 “대통령”이라는 단어로 만들어낼 수 있습니다. 
처음에는 Stop words와 다른 방식들을 이용하여 normalizing 과정을 진행하려하였으나 정확도가 높게 나오지 않았으며 한국어의 형태소 분석을 직접 설계하여 실행하는 것은 프로그램의 real time 측면에서 좋지 않을 것이라고 판단하여 제외하였습니다.
이렇게 국어 사전 api는 네이버 백과사전의 api를 가져와 사용하였습니다. 하지만 여기서 문제가 하나 발생하였습니다. 무료로 진행되는 api인만큼 하루 25000건의 검색을 제공하는데 현재 full corpus의 단어들의 총 개수는 약 15000개입니다. 따라서 2번 이상 full corpus에 대한 검색을 진행하면 하루 제공 검색량을 초과하여 사전 api를 이용할 수 없게 됩니다. 이에 대한 해결책으로 프로그램 최초 실행 1회에 한하여 검색을 진행하고 검색의 결과를 파일로 저장하고자 하였습니다.
따라서 만약 검색 결과를 저장한 파일이 존재한다면 1)의 검색 과정을 생략하고 진행하게 됩니다. 바로 2)로 진행되게 됩니다.
쿼리를 사전 api로 request를 보내면 해당 쿼리에 대한 검색 결과가 json 형식으로 받을 수 있습니다. 이를 parsing하여 원하는 정보만을 추출한 다음 String에 관한 처리를 진행하면 쿼리의 normalizing한 결과를 얻을 수 있게 됩니다.
사용한 api의 url에 대해서 잠깐 살펴보자면 다음과 같습니다.
"https://openapi.naver.com/v1/search/encyc?query="
query뒤에 원하는 단어를 넣어주고 request를 보내면 다음과 같은 형태로 정보가 들어옵니다. 
```
{
	"lastBuildDate":"Mon, 06 Jun 2022 15:43:46 +0900",
	"total":51448,
	"start":1,
	"display":10,
	"items":[
		{ "title":"<b>대통령<\/b>",
"link":"https:\/\/terms.naver.com\/entry.naver?docId=1081578&cid=40942&categoryId=31645",
		  "description":"&#60;헌법상의 지위&#62; <b>대통령<\/b>의 헌법상의 지위는 집행권의 구조에 따라 다르다. 집행권이 일원적 구조에 입각하고 있는 경우에는 미국형 <b>대통령<\/b>제에서와 같이 입법부 ·사법부와 함께 동렬(同列)에 위치한다. 그러나... ",
		   "thumbnail":""
		}, (생략…)
	]
}
```
생략한 부분에는 items의 내용들에 해당하는 title, description, thumbnail의 정보가 있는 추가적인 검색 결과들이 있습니다.

2) normalizing된 단어들을 이용하여 tf-idf 계산

이렇게 normalizing된 단어들을 이용하여 각 문서에 대한 Term frequency를 계산하고 각 Term에 대한 Document frequency도 계산한 후 tf-idf matrix를 작성하게 됩니다. 여기서 idf값은 분모가 0이되어 에러를 발생하는 것을 막기 위해서 log(N/(1+df))로 진행하였습니다. 

3) 입력된 쿼리 또한 normalizing

입력된 쿼리도 normalizing 시켜야 corpus안에 있는 다른 단어들과 매칭시킬 수 있다고 생각했습니다. 따라서 1)과정에서 진행했던 내용들을 그대로 입력 쿼리에 적용시켜서 쿼리 또한 normalizing된 결과를 가질 수 있도록 하였습니다. 이는 검색 결과 속도를 더 빠르게 해줄 것이라고 생각합니다.

4) 쿼리가 포함된 문서들의 tf-idf 가중치 값을 바탕으로 점수 계산

Normalizing된 쿼리를 전달받았다면 이제 어떠한 문서가 높은 점수를 가지게 되는가에 대해서 알아봐야합니다. 사전에 있는 결과로 단어들을 normalzing했기에 100%일치하는 단어들이 있는지 판별해주면 된다고 생각했습니다. 따라서 어떠한 문서에 쿼리 안에 있는 단어가 존재한다면 해당 문서에게 tf-idf값을 더해주는 과정을 거쳤습니다. 
이 과정을 거치면 문서들에 대한 점수들이 모두 구해지게 되며 이들은 실수 값을 가지게 됩니다.

5) 결과 출력

문서들에 대한 점수들이 모두 구해지게 되면 남은 것은 결과를 출력하는 것입니다. 점수를 기준으로 문서를 정렬하여 가장 높은 값을 가지는 문서 5개를 골라서 화면에 출력해줍니다. 
프로그램이 얼마나 오랫동안 실행되었는지에 대해 알아보기 위해서 time을 통해 시작 시간과 종료 시간을 구하였습니다. 함수가 돌아가는 시간만을 계산하였으며 사용자가 입력을 마치는 시간은 제외하였습니다.

3. 관련 자료

아래는 프로그램을 만드는데 도움이 되거나 참고한 자료들의 모음입니다. 어떠한 api를 사용했는지 어떠한 문서를 참고했는지 확인하실 수 있습니다.

1) 네이버 백과사전 검색 api

https://developers.naver.com/docs/common/openapiguide/apilist.md#%EB%B9%84%EB%A1%9C%EA%B7%B8%EC%9D%B8-%EB%B0%A9%EC%8B%9D-%EC%98%A4%ED%94%88-api

2) 파이썬 document

https://docs.python.org/ko/3/

4. 실행 결과

처음 프로그램을 실행하여 dictionary.json을 만들 때에는 api가 제공하는 검색 속도의 한계로 인해 약 14분의 시간이 걸렸습니다. 하지만 해당 파일을 바탕으로 검색을 진행할 때에는 2초 이내의 매우 빠른 검색시간을 보여주었습니다. 처음 실행하는 과정을 서버가 진행해준다면 실제 user가 사용하기에는 불편함이 없을 속도라고 생각합니다.
Cosine 을 비롯해 추가적인 보완 함수를 추가한다면 더욱 정확하고 정밀한 결과를 가져올 수 있을 것으로 기대됩니다.

* 이상으로 정보검색 과제에 대한 보고를 마치겠습니다. 감사합니다.
Date : 2022-06-06
