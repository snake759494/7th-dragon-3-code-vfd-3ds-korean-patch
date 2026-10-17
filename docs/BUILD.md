# 빌드 방법

번역 대본·원문·튜토리얼 편집 명세는 저장소에 없으므로, 아래는 자신이 가진 원본과 번역 파일로 다시 빌드하는 절차입니다.

## 준비물
- 원본 `7th Dragon III Code - VFD (Japan).3ds` (MD5 `0534966ca3b60a468e424b12cb59c82b`)
- Python 3.12+ : `pip install pillow numpy opencv-python-headless capstone`
- 글꼴 `NanumSquareNeo-bRg/cBd/dEb/eHv.ttf`, `SeoulHangangEB.ttf`

## 폴더 구성
```
<작업 폴더>/                원본 .3ds, 글꼴
  <이 저장소>/
    tools/
    ext/  cpk/  code.bin    추출물 (아래 1단계)
    tr/catalog.json         추출한 원문 목록
    tr/out/*.json           번역 {id: 한국어}
    tr/area.txt             지역명 (파일명<TAB>상단<TAB>하단)
    tools/tutspec.py        튜토리얼 글자 상자 명세(선택)
```

## 순서
1. 추출: `python tools/ctr.py "<원본>.3ds" ext`, `python tools/cpk.py ext/romfs/cpk/eden_files.cpk cpk`, `code.bin`은 `tools/codeblz.py`의 `decompress`로 `ext/exefs/.code`를 풀어 저장
2. 원문 목록·번역 묶음: `python tools/extract.py` → `tr/catalog.json`, `tr/in/*.json`
3. 번역 작성 후 검사: `python tools/check_tr.py <묶음번호>`
4. 빌드: `python tools/build_all.py` → 작업 폴더에 `7th Dragon III Code - VFD (Korean).3ds`
5. 차분: `xdelta3 -e -s 원본.3ds 한글.3ds 패치.xdelta` (압축 옵션 없이)

에뮬레이터 확인(`launch.py`, `s2.py`)은 Azahar가 한글 경로에서 실행되지 않으므로 ASCII 경로의 junction을 만들고 `AZ_WORK` 환경 변수로 지정하세요.
