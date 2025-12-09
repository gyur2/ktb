# 🍊 과즙상 커뮤니티 

FastAPI를 사용해 구현한 과일 닮은꼴 커뮤니티 사이트입니다.
개발은 초기 프로젝트 화면부터, 기능, 백엔드 연결까지 직접 구현했습니다.

## 개발 인원 및 기간
- 개발기간 : 2025-12-01 ~ 2025-12-02
- 개발 인원 : 프론트엔드/백엔드 1명 (본인)

## 사용기술 및 Tools
- Vanilla js
  
## 백엔드
- <a href="https://github.com/gyur2/ktb/tree/main/12WEEK/backend">Backend Github</a>
---

## 폴더 구조
<details>
  <summary>폴더 구조 보기/숨기기</summary>
  <div markdown="1">

    ├── js/
    |  ├── app.js
    |  ├── auth.js
    |  ├── board.js
    |  ├── home.js
    |  └── profile.js
    ├── index.html
    └── style.css

  </details>
  <br/>
  
## 서비스 화면
`홈`
|로그인|회원가입|홈|
|---|---|---|
|![로그인](https://github.com/user-attachments/assets/4a0e1aa4-f184-4140-9fcd-41fdeafebdd7)|![회원가입](https://github.com/user-attachments/assets/10897ccb-7055-46fd-9676-d705a297a236)|![홈](https://github.com/user-attachments/assets/b136d0d5-5443-4210-b344-51887a5f7c2c)|

`게시글 목록`
|게시판|게시글 상세|게시글 작성|
|---|---|---|
|![게시판](https://github.com/user-attachments/assets/15e8b89e-98a8-498f-9cee-596a6d6b4a56)|<img width="404" height="569" alt="게시글 상세페이지" src="https://github.com/user-attachments/assets/3be83777-1913-44bf-bf6e-54949f0db626" />|<img width="393" height="493" alt="게시글 작성" src="https://github.com/user-attachments/assets/0e24ce6a-e051-4c2a-8b38-dfd9128b5102" />|

## 트러블 슈팅 
1. 이미지 업로드 시 개발 서버 무한 재로딩 현상
2. 로컬 파일 보안 정책(Fakepath) 및 이미지 안 뜨는 문제
3. API 요청 헤더(Header) 및 데이터 포맷 충돌

## 프로젝트 후기
평소에 웹 페이지를 개발할 때 vanilla가 아닌 React 라이브러리를 사용해서 개발을 하는데, 요번 프로젝트는 vanilla만 사용해서 개발을 했습니다. vanilla에서는 훅을 사용하지 못하기 때문에 훅처럼 동작하는 코드를 만들기 위해 어떻게 해야하나 고민도 많이해보게 된 프로젝트였던 것 같습니다. 프로젝트를 하면서 javascript 동작 방식에 대해서 좀 더 이해하게 되었습니다. 좀 더 많은 기능을 추가하고 싶었으나 아이디어 부족으로 인해, 기능 추가를 하지 못한 점이 아쉬운 것 같습니다. 다음 프로젝트에서는 여러 핵심 기능을 구현하고, 현재 습득한 기술 및 지식을 활용하여 프로젝트를 진행하도록 하겠습니다.
