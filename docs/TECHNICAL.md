# 기술 문서

## ROM 구조
- NCSD → NCCH 0. 원본 덤프는 이미 복호화(NoCrypto) 상태입니다.
- romfs에는 `cpk/eden_files.cpk` 하나만 있습니다(CRI CPK, 무압축, Align 512, 파일 4,849개).
- 수정한 파일은 CPK 끝(ETOC 앞)에 덧붙이고 TOC의 `FileOffset/FileSize/ExtractSize`와 헤더의 `EtocOffset/ContentSize`만 고칩니다. ITOC는 ID→TOC 인덱스 표뿐이라 손댈 필요가 없습니다(`tools/cpkpack.py`).
- romfs(IVFC 해시)·exefs·NCCH·NCSD를 다시 만듭니다(`tools/build.py`). 실행 코드는 BLZ 압축을 풀어 비압축으로 넣습니다.

## 텍스트
| 파일 | 형식 | 처리 |
| --- | --- | --- |
| `text/JP/Mess*.dat` (22개) | 헤더 a,b,c / u32 오프셋[(b-a)/4] / UTF-16 문자열(문자 단위 오프셋) | 전체 재작성 (`tools/mess.py`) |
| `db/TownText.bin`, `questText1.bin`, `staffrollText.bin` | u32 개수 + (id, 바이트 오프셋) + UTF-16 | 전체 재작성 |
| `db/b_battle1.bin` | u16 개수 + u32 id[] + u16 오프셋[] + UTF-16 | 전체 재작성 |
| `item/itemData.bin` | 그룹별 고정 크기 레코드(이름 32바이트, 설명 96바이트) | 제자리 교체 |
| `btparam/enemy_list.bin` | BOM(FFFE)으로 시작하는 순차 문자열 | 제자리 교체 |
| UI 레이아웃 `ui/layout/*.arc` (SARC → BFLYT txt1) | UTF-16, 버퍼 크기 고정 | 제자리 교체, textStrBytes 갱신 |
| `code.bin` | UTF-16 문자열 9곳 | 같은 길이 안에서 교체 |

제어 코드: `<COL=RED>` 등 색 태그, `\x08\x01`·`\x08\x02`(이름 변수), `＠이름`(화자 줄), `#dst`·`#src`(전투 대상).

## 폰트
- 대사창은 `font/12font.bffnt`(BFFNT v4, A4, 1024×1024 시트 1장, 13×16 칸 4,380자)를 씁니다. 가나·기호는 그대로 두고 한자 자리를 한글 2,350자(+사용된 자모)로 바꿔 시트 1장 안에 넣었습니다(`tools/mkffnt.py`).
- UI 레이아웃은 원래 시스템 공유 폰트(`cbf_std`)를 씁니다. 폰트 로더(0x20974c)는 이름이 NULL이면 공유 폰트를 쓰므로, 호출부 0x10e2b4의 4명령을 `add r1,r4,#0x140 / sub r2,pc,#0x2a00 / sub r2,r2,#0x6f / bl` 로 바꿔 `font/12font.bffnt`를 읽게 했습니다(`tools/codepatch.py`).

## 그림 글자
- BFLIM 디코드/인코드: `tools/texpatch.py` (swizzle 4 = 90° 회전, swizzle 8 = 상하반전 후 −90° 회전), ETC1/ETC1A4 인코더 `tools/etc1enc.py`.
- 지역명 192장(`ui/areatitlelist`): 어두운 띠형/밝은 이탤릭형 두 가지 양식을 새로 렌더링(`tools/areaimg.py`).
- 던전 진입 지명 카드(`a_common_locationtitle_*.arc`): BFLYT의 pic1 판(위치·크기·UV)을 해석해 원래 합성 화면을 재현하고, 판마다 한글 조각을 그려 해당 UV 영역에 되돌려 넣었습니다(`tools/loca.py`).
- 튜토리얼·체험판 안내: 글자 상자 단위로 글자 픽셀만 인페인트로 지우고 같은 색 한글을 그렸습니다(`tools/tut.py`).
- 로고 부제·체험판 표기, 층 표시, 도움말, 세계지도, 주의 문구, 스킬 배지: `tools/arcimg.py`.

## 홈 메뉴
- SMDH 일본어 제목 칸을 영문 제목으로 바꿨습니다(일본 본체 시스템 폰트에 한글이 없음).
