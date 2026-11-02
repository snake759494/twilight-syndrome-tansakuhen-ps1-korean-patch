# 트와일라잇 신드롬 ~탐색편~ PS1 한글패치

PS1 일본판 **トワイライトシンドローム ～探索編～ (SLPS-00102)**용 비공식 한국어 패치입니다. 시작의 소문부터 또 하나의 소문까지 **모든 챕터의 대사·선택지**를 한국어로 바꿨습니다. **타이틀 메뉴, 세로쓰기 챕터 제목, 챕터 타이틀 카드, 장소 이름, 메모리 카드 안내, 게임오버 메시지 같은 그림 글자**도 한글로 다시 그렸습니다. 현재 배포판은 **v1.1 (2026-11-02)**입니다.

[패치 다운로드](https://github.com/snake759494/twilight-syndrome-tansakuhen-ps1-korean-patch/releases/latest) · [기술 설명](docs/TECHNICAL.md) · [재빌드](docs/BUILD.md) · [변경 기록](CHANGELOG.md) · [권리 안내](RIGHTS.md)

릴리즈 첨부 파일은 한글패치 **TwilightSyndrome_Tansakuhen_PS1_KO_v1.1.xdelta**뿐입니다. 저장소에는 제작 소스와 한국어 번역만 공개합니다. 원본·완성 디스크 이미지, 추출한 게임 파일, 일본어 원문, 글꼴 파일, 외부 실행 파일은 포함하지 않습니다. GitHub가 자동으로 만드는 Source code ZIP/TAR는 저장소 소스를 압축한 것이며 게임 파일이 아닙니다.

## 게임 소개 및 대상 버전

『トワイライトシンドローム ～探索編～』은 휴먼이 1996년에 PS1으로 낸 호러 어드벤처 게임입니다. 히나시로 고교의 여고생 유카리·치사토·미카가 학교와 마을에 떠도는 소문을 조사하며 괴이한 사건에 휘말리는 이야기로, 횡스크롤 탐색과 선택지로 진행합니다.

이 패치는 **PS1 일본판 SLPS-00102의 BIN/CUE 이미지(단일 트랙, MODE2/2352)**에만 적용됩니다. 파일 이름보다 아래 표의 크기와 해시가 일치하는지가 중요합니다.

## 적용할 원본

| 항목 | 값 |
| --- | --- |
| 게임 ID | SLPS-00102 |
| 원본 형식 | 수정되지 않은 일본판 BIN/CUE (트랙 1개) |
| 원본 BIN 크기 | 636,488,832 바이트 |
| **원본 BIN MD5** | `94de7fb58c36e70de87124d471eae1b8` |
| 원본 BIN SHA-1 | `7f11266e64793184dea33ebef291cdd9c68d3c2d` |
| 원본 BIN SHA-256 | `44f292433547ee8b478f8103e78cd3a00acae7e72c8ac414fda931c09d719364` |
| xdelta 파일 크기 | 854,772 바이트 |
| xdelta SHA-256 | `f03032cb20818f505e864ec4f70418f37cb652936f428f98fdd428270fcfd4a6` |
| 적용 결과 BIN 크기 | 636,488,832 바이트 (원본과 같음) |
| 적용 결과 BIN SHA-1 | `0736ff1c517fe9db4137bcc5faae48bfffc0f117` |
| 적용 결과 BIN SHA-256 | `16ac03f6d5290f760bf7cfdede580a3fb603d0da883f0fb4a6b0677f7e912d9c` |

원본 게임 파일은 사용자가 직접 준비해야 합니다.

## 패치 적용 방법

### Windows에서 원본 확인

```powershell
Get-FileHash -Algorithm MD5 -LiteralPath '.\Twilight Syndrome - Tansaku-hen (Japan).bin'
```

위 표와 다르면 적용을 중단하세요. CHD, PBP, ECM, 압축 이미지에는 적용할 수 없습니다.

### xdelta UI 사용

1. 릴리즈에서 `TwilightSyndrome_Tansakuhen_PS1_KO_v1.1.xdelta`를 받습니다.
2. xdelta3 패치를 지원하는 도구에서 **Apply Patch** 기능을 엽니다.
3. **Patch**에는 xdelta 파일을, **Source File**에는 해시가 일치하는 원본 `.bin`을 선택합니다.
4. **Output File**에는 새 파일 이름을 지정합니다(예: `Twilight Syndrome - Tansaku-hen (Korean).bin`).
5. 원본 `.cue`를 복사해 결과 BIN과 같은 이름으로 바꾸고, 안의 `FILE "..."` 줄을 결과 BIN 파일 이름으로 고칩니다.

```
FILE "Twilight Syndrome - Tansaku-hen (Korean).bin" BINARY
  TRACK 01 MODE2/2352
    INDEX 01 00:00:00
```

xdelta는 호환성을 위해 압축·2차 압축·파일 경로 헤더 없이 만들었습니다. xdelta 자체는 [공식 프로젝트](https://github.com/jmacd/xdelta)를 참고하세요.

### 명령줄 사용

```powershell
.\xdelta3.exe -d -s '.\Twilight Syndrome - Tansaku-hen (Japan).bin' '.\TwilightSyndrome_Tansakuhen_PS1_KO_v1.1.xdelta' '.\Twilight Syndrome - Tansaku-hen (Korean).bin'
```

해시를 자동으로 검사하고 CUE까지 만들어 주는 도구도 있습니다. Python 3과 xdelta3가 필요하며, 같은 이름의 출력 파일이 이미 있으면 덮어쓰지 않습니다.

```powershell
python tools/apply_release.py --xdelta '.\xdelta3.exe' --source '.\Twilight Syndrome - Tansaku-hen (Japan).bin' --patch '.\TwilightSyndrome_Tansakuhen_PS1_KO_v1.1.xdelta' --output '.\Twilight Syndrome - Tansaku-hen (Korean).bin'
```

### 실행

에뮬레이터에서 결과 `.cue`를 여세요. 원본판의 세이브 스테이트는 불러오지 마세요(실행파일과 데이터 내용이 다릅니다). 메모리 카드 세이브는 원본판과 같은 형식이라 그대로 쓸 수 있을 것으로 보지만, 직접 확인하지는 못했습니다.

## 작업 내용과 범위

| 구분 | 작업량 및 내용 |
| --- | --- |
| 대사·선택지 | 6개 챕터 대본 스크립트 10개, 대사 블록 1,178개 전체 |
| 글꼴 | 대사창 16×16 한글 비례폭 글꼴(나눔스퀘어 네오 Bold), 챕터별 522~744자 |
| 그림 글자 | 타이틀 「시작/준비」, 옵션 메뉴(창 색상·메시지 타입·기억 회상 등), 세로쓰기 챕터 제목 6장, 챕터 시작 타이틀 카드 6장, 장소·소리 이름 29개, 전리품 메뉴, 메모리 카드 안내 18종, 게임오버 메시지 |

일본어 전용 게임에 한글을 표시하기 위해 챕터별 글꼴 데이터를 새로 만들고, 실행파일의 글꼴 표 참조와 대본 블록 포인터를 고쳤습니다. 자세한 내용은 [docs/TECHNICAL.md](docs/TECHNICAL.md)를 참고하세요.

### 번역 원칙

- 기계 번역 없이 문맥을 보고 직접 번역했습니다.
- 인명은 일본어 발음대로 적었습니다(하세가와 유카리, 이쓰시마 치사토, 기시이 미카 등).
- 대사창 폭(한 줄 272픽셀)과 원문의 줄 수·제어 코드에 맞춰 줄을 나눴습니다.

### 번역하지 않은 것

- 음성, 동영상
- 배경 그림 속 간판·셔터 등의 글씨
- 제작사 로고, 저작권 표기

## 알려진 한계

- 모든 화면을 직접 확인하지는 못했습니다. 첫 장면의 대사 출력은 에뮬레이터로 확인했지만, 다시 그린 메뉴·챕터 제목·타이틀 카드·게임오버 화면은 게임 화면으로 보지 못했습니다. 칸을 넘치거나 어긋난 문구가 있으면 이슈로 알려 주세요.
- 일부 선택지는 칸 폭 때문에 원문보다 짧게 줄였습니다.
- 인게임 확인은 DuckStation으로 했습니다. 실기에서의 동작은 확인하지 못했습니다.

## 저장소 구성

| 경로 | 내용 |
| --- | --- |
| `build.py` | 전체 빌드(대본 재구성, 글꼴 생성, 실행파일·CDB 교체) |
| `tools/` | 빌드·검증 도구(Python). `kfont.py` 한글 글꼴, `gfxpatch.py` 그림 글자, `lz.py` 압축, `chk.py` 번역 검사, `apply_release.py` 해시 검사 후 적용, `emu.py` DuckStation 테스트 조작 |
| `text/ko/` | 번역. 대본별 `{"id": 블록 번호, "ko": 번역}` |
| `fonts/` | (저장소에 없음) 갈무리 글꼴을 두는 곳 |
| `docs/` | 기술 설명, 재빌드 방법, 글꼴 출처 |

권리 관련 내용은 [RIGHTS.md](RIGHTS.md)를 참고하세요.
