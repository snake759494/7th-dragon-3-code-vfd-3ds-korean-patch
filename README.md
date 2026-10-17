# 세븐스 드래곤 III code:VFD (3DS) 비공식 한글패치

닌텐도 3DS 일본판 **セブンスドラゴンIII code:VFD** (CTR-P-BD7J) 비공식 한국어 패치입니다. 이 저장소에는 제작 도구와 기술 문서만 있고, 패치 파일(xdelta)은 [Releases](../../releases)에서 받을 수 있습니다. 게임 원본·일본어 원문·번역 대본은 포함하지 않습니다.

## 적용 방법
1. 아래 해시와 일치하는 **원본 `.3ds`**(복호화된 카트리지 덤프, 2GB)를 준비합니다. CIA나 암호화된 덤프에는 적용할 수 없습니다.
   - PowerShell: `Get-FileHash -Algorithm MD5 -LiteralPath '.\7th Dragon III Code - VFD (Japan).3ds'`
2. xdeltaUI 같은 도구로 원본에 `7thDragon3_VFD_3DS_KO_v1.1.xdelta` 를 적용합니다.
   - 명령줄: `xdelta3 -d -s "7th Dragon III Code - VFD (Japan).3ds" 7thDragon3_VFD_3DS_KO_v1.1.xdelta "7th Dragon III Code - VFD (Korean).3ds"`
3. 만들어진 `.3ds`를 Azahar 등 3DS 에뮬레이터에서 실행합니다.

| 항목 | 값 |
| --- | --- |
| 원본 3DS 크기 | 2,147,483,648 바이트 |
| 원본 3DS MD5 | `0534966ca3b60a468e424b12cb59c82b` |
| 원본 3DS SHA-256 | `5ac16175c110f15145d113ae9276343fcd5d73c55c55c1084148b73b5af4b2eb` |
| xdelta 크기 | 56,301,452 바이트 |
| xdelta SHA-256 | `a6293ae5ba423508c125de8e0d28c889cc863af901843eba2e7da4f763527266` |
| 결과 3DS 크기 | 1,759,817,728 바이트 |
| 결과 3DS SHA-256 | `e421ebc25f12c6d4cf653e6e9cd44eb7d91a999fe573b6f0055383aac5326bea` |

## 주의
- 결과 파일은 복호화 상태(NoCrypto)이고 실행 코드(`.code`)를 비압축으로 넣었습니다. 실기(Luma3DS 등 커스텀 펌웨어)에서 쓸 수 있도록 익스헤더·ExeFS·RomFS(IVFC 전 계층) 해시와 NCSD/NCCH 헤더를 규격대로 다시 계산했고 `tools/verify.py`로 전부 검증했습니다. 플래시카트에 넣거나 GodMode9에서 CIA로 변환해 설치할 수 있습니다. 실기 실행 자체는 제작 환경에 기기가 없어 직접 확인하지 못했습니다.
- 결과 파일은 원본의 빈 공간(패딩)을 잘라내 원본보다 작습니다.
- 홈 메뉴 제목은 일본 본체 시스템 폰트에 한글이 없어 영문 제목(`7TH DRAGON Ⅲ code:VFD`)으로 바꿨습니다.
- 이름 입력은 3DS 시스템 소프트웨어 키보드를 씁니다. 게임은 한글 이름을 표시할 수 있으며, 에뮬레이터에서는 한글을 바로 입력할 수 있습니다(일본 본체의 시스템 키보드로는 한글 입력 불가).

## 한글화 내용
- 게임 텍스트 고유 문장 16,261개: 대사·이벤트, 필드 메시지, 스킬·아이템·적 이름과 설명, 퀘스트, 메뉴, 전투 메시지, 스태프롤, 디버그 메뉴
- UI 레이아웃 문구, 실행 코드(code.bin) 안의 문구
- 그림 글자: 타이틀 로고 부제·체험판 표기, 지역명 192장, 던전 진입 지명 카드 12종, 챕터 부제 10장, 튜토리얼 41장, 체험판 안내 7장, 층 표시·아이템 도움말·세계지도·주의 문구·스킬 배지 등
- 게임 폰트(12font, 13×16)에 한글 KS X 1001 2,350자(나눔스퀘어네오 Bold). UI 레이아웃이 쓰던 시스템 공유 폰트 대신 이 폰트를 읽도록 실행 코드를 패치

## 그대로 둔 것
- 크레딧 그림 속 인명 한자 한 곳
- 데이터로 쓰이는 것으로 보이는 한자 몇 글자짜리 문자열 9개

## 검증 범위
Azahar에서 부팅, 타이틀, 새 게임, 오프닝 대사, 캐릭터 생성·한글 이름 입력까지 확인했습니다. 전체 플레이 검증은 하지 않았습니다. 문제를 발견하면 Issues에 알려 주세요.

## 문서
- [CHANGELOG.md](CHANGELOG.md) — 변경 기록
- [docs/TECHNICAL.md](docs/TECHNICAL.md) — 파일 형식과 한글화 방법
- [docs/BUILD.md](docs/BUILD.md) — 직접 빌드하는 방법
- [docs/FONT_CREDITS.md](docs/FONT_CREDITS.md) — 글꼴
- [RIGHTS.md](RIGHTS.md) — 권리 및 외부 자료
