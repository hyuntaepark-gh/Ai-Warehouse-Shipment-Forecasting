# Warehouse IQ — GitHub 업로드 안내

## 1. 압축 풀기

`Warehouse-IQ-GitHub-Ready.zip`을 압축 해제하면 `Warehouse-IQ` 폴더가 생성됩니다. 폴더 안에 `app.py`, `README.md`, `requirements.txt`, `capstone_final_outputs/`, `foundation_summaries/`, `docs/`, `tests/` 등이 있어야 합니다. **ZIP 파일만 그대로 업로드하면 GitHub가 코드를 개별 파일로 표시하지 않습니다.**

## 2. 업로드 전에 Windows에서 실행 확인

`Warehouse-IQ` 폴더에서 PowerShell을 열고 실행합니다.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python verify_release.py
python -m unittest discover -s tests -v
python -m streamlit run app.py
```

브라우저에서 `http://localhost:8501`에 접속해 **8개 메뉴, KPI(12.35%), 모든 그래프, 필터 및 CSV 다운로드**를 확인하세요. 압축 정리로 분석용 `.py`와 원본 출력 데이터의 내용을 변경하지 않았지만, 이 배포본에 대한 Streamlit 전체 테스트/브라우저 실행은 아직 직접 확인되지 않았습니다.

## 3. GitHub에서 저장소 만들기

1. GitHub 로그인 → 오른쪽 상단 `+` → `New repository`.
2. 추천 저장소 이름: `Warehouse-IQ`.
3. 설명 예시: `Interactive supply chain demand forecasting dashboard built with Python, Streamlit, and Plotly.`
4. 공개 여부를 결정하기 전에 사용한 데이터·그래프의 재배포 권한과 학교 제출/공개 규정을 확인하세요.
5. `Add a README file`은 체크하지 말고 저장소를 만듭니다. 이 패키지에 이미 README가 있습니다.

## 4. 파일 업로드

이 프로젝트는 파일이 많으므로 **GitHub Desktop 또는 Git 명령어로 업로드하는 방식을 권장**합니다. 웹 브라우저의 `Upload files` 기능은 한 번에 올리는 파일 수에 제한이 있을 수 있습니다. 압축 파일 자체를 저장소에 올리는 방식은 추천하지 않습니다.

GitHub Desktop에서 `File → Add Local Repository`를 선택하고, 압축 해제한 `Warehouse-IQ` 폴더를 지정하세요. Git 저장소가 아니라는 안내가 나오면 새 저장소 생성을 선택한 뒤 첫 커밋을 만듭니다. 그다음 `Publish repository`에서 공개/비공개 설정을 확인하고 업로드합니다. 3단계에서 이미 빈 GitHub 저장소를 만들었다면 그 저장소로 푸시하거나, GitHub Desktop에서 별도로 새 저장소를 공개하는 방식 중 하나만 사용하세요.

Git 명령어를 직접 사용하려면 다음과 같이 실행합니다:

```bash
git init
git add .
git commit -m "Publish Warehouse IQ dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/Warehouse-IQ.git
git push -u origin main
```

`YOUR-USERNAME`을 실제 GitHub 사용자 이름으로 바꾸세요. 기존 원격 저장소를 사용 중이면 `git remote add origin`을 중복 실행하지 마세요. `Warehouse-IQ` 폴더 안에서 명령어를 실행해야 파일들이 저장소 루트에 표시됩니다. 특히 `.streamlit/config.toml`과 `.gitignore` 같은 숨김 항목도 포함되어야 합니다.

## 5. GitHub 화면에서 확인

저장소 첫 화면에 `README.md`의 영어 소개·대시보드 스크린샷이 보여야 합니다. 루트에 `app.py`가 바로 보이는지 확인하세요. GitHub에 업로드만 하면 Streamlit 웹앱이 자동으로 실행되는 것은 아닙니다.

실행 가능한 공개 링크가 필요하다면 Streamlit Community Cloud 등의 환경에서 저장소와 `app.py`를 연결해 별도로 배포할 수 있습니다. 배포 시 공개 데이터 권한과 로컬 실행 결과를 먼저 확인하세요.

## 정리 내용

- 제외: `__pycache__`, `.ui_backup`, 이전 수정 스크립트, 오래된 임시 안내/테스트 로그
- 유지: 현재 앱 코드, 87개 Capstone 원본 결과 파일, 모든 데이터 요약, 테스트/검증 자료
- 추가: 영어 포트폴리오 README, Overview 스크린샷, GitHub 업로드 안내, 개선한 `.gitignore`
- 경로: 문서에 남아 있던 개인 PC 절대 경로를 상대 경로 예시로 정리
- 이전 상세 README는 `docs/PROJECT_BUILD_HISTORY.md`에 보관
