# GitHub 초보자 가이드 — 이 포트폴리오를 처음 올리는 방법

## 0. 현재 폴더 상태

2026-08-18 점검 기준:

- 로컬 Git 저장소: 이미 있음 — **`git init`을 다시 실행하지 않아도 됨**
- 현재 브랜치: `master` — 첫 공개 전에 `main`으로 변경 권장
- GitHub 원격 저장소: 아직 연결되지 않음
- Git 작성자 이름/이메일: 아직 설정되지 않음
- 파일 상태: `project_01_molding/`이 아직 untracked이며 첫 commit 전

여기서 Git은 내 PC의 변경 이력 도구이고, GitHub는 그 저장소를 온라인에 보관·공유하는 서비스다.

```text
작업 폴더 → git add(선택) → git commit(로컬 저장) → git push(GitHub 전송)
```

## 1. 공개 전 보안 점검

공개 portfolio라면 다음을 먼저 확인한다.

- 실제 회사/Fab 데이터, recipe, 고객명, 사번, 개인 연락처가 없는가?
- API key, 비밀번호, `.env`, 인증서가 없는가?
- 다운로드한 논문 PDF나 재배포 권한이 없는 자료를 넣지 않았는가?
- synthetic data임을 README에 명확히 썼는가?

현재 `.gitignore`는 `.env`, virtual environment, Python cache, Jupyter checkpoint 등을 제외한다. 단, `.gitignore`는 이미 commit된 비밀을 지워 주는 도구가 아니다. 첫 push 전에 반드시 파일 목록을 직접 확인한다.

PowerShell에서:

```powershell
cd "C:\Users\User\Documents\ChatGPT\후공정프로젝트"
git status
git status --short
```

`??`는 아직 Git이 추적하지 않는 새 파일이라는 뜻이다. 현재는 정상이다.

## 2. 추천 방법 — GitHub Desktop

명령어와 인증이 낯설다면 이 방법이 가장 쉽다.

### 2-1. 설치와 로그인

1. [GitHub Desktop](https://desktop.github.com/)을 설치한다.
2. 실행 후 GitHub 계정으로 로그인한다.
3. 처음 묻는 Git 작성자 이름/이메일을 설정한다.
4. 이메일 공개가 싫다면 GitHub 웹의 `Settings → Emails`에서 제공하는 `noreply` 주소를 사용한다.

Git의 작성자 이름은 GitHub 로그인 아이디와 같을 필요가 없다. 다만 portfolio에서는 본인을 알아볼 수 있는 일관된 이름을 권장한다.

### 2-2. 기존 로컬 저장소 추가

1. GitHub Desktop에서 `File → Add Local Repository`를 누른다.
2. Local Path에 다음 폴더를 선택한다.

   `C:\Users\User\Documents\ChatGPT\후공정프로젝트`

3. `Add Repository`를 누른다.
4. 왼쪽 `Changes` 탭에서 공개될 파일을 하나씩 확인한다.

이 폴더에는 이미 `.git`이 있으므로 `Create a New Repository`가 아니라 **Add Local Repository**를 사용한다.

### 2-3. 첫 commit

1. 변경 파일 목록에서 `.gitignore`, 루트 `README.md`, `project_01_molding/`만 포함됐는지 확인한다.
2. 왼쪽 아래 Summary에 다음처럼 입력한다.

   `Add compression molding engineering portfolio`

3. `Commit to master`를 누른다.
4. 상단 메뉴 `Branch → Rename`에서 `master`를 `main`으로 바꾼다.

Commit은 아직 내 PC에만 저장된 스냅샷이다. 이 단계까지는 GitHub 웹에 공개되지 않는다.

### 2-4. GitHub에 publish

1. 상단 `Publish repository`를 누른다.
2. Name 예시: `semiconductor-packaging-engineering-portfolio`
3. Description 예시: `Physics-informed Package & Test engineering portfolio using synthetic data`
4. 취업 portfolio로 공개하려면 `Keep this code private` 체크를 해제한다.
5. Organization은 개인 계정으로 둔다.
6. `Publish Repository`를 누른다.

공개가 부담스럽다면 먼저 Private으로 올려 검토한 뒤 GitHub 웹 `Settings → General → Danger Zone → Change repository visibility`에서 Public으로 바꿔도 된다.

### 2-5. 이후 수정 반영

1. 로컬 파일을 수정한다.
2. GitHub Desktop `Changes`에서 diff를 읽는다.
3. 변경 목적을 한 문장으로 Summary에 쓴다.
4. `Commit to main`을 누른다.
5. `Push origin`을 누른다.

Commit message 예시:

- `Clarify synthetic data limitations`
- `Add surface roughness validation plan`
- `Update confirmation figures`
- `Fix README navigation`

## 3. PowerShell 방법 — Git 원리까지 배우기

GitHub Desktop 경로와 **둘 중 하나만** 선택하면 된다. 아래 명령에서 `YOUR_GITHUB_USERNAME`과 이메일은 본인 값으로 바꾼다.

### 3-1. 작성자 정보 설정

이 저장소에만 적용하려면 `--global` 없이 설정한다.

```powershell
cd "C:\Users\User\Documents\ChatGPT\후공정프로젝트"
git config user.name "YOUR NAME"
git config user.email "YOUR EMAIL OR GITHUB NOREPLY EMAIL"
```

모든 PC 저장소에 같은 값을 쓰려면 `git config --global ...`을 사용한다. 이메일 privacy가 필요하면 GitHub 웹 `Settings → Emails`에서 본인 계정에 표시된 noreply 주소를 그대로 복사한다.

값을 노출하지 않고 설정 여부만 확인하려면:

```powershell
git config --get user.name
git config --get user.email
```

이 명령은 실제 값을 화면에 표시하므로 화면 공유 중에는 주의한다.

### 3-2. 첫 commit 만들기

```powershell
git status --short
git add .gitignore README.md project_01_molding
git status
git diff --cached --stat
git commit -m "Add compression molding engineering portfolio"
git branch -M main
```

각 명령의 의미:

- `git add`: 다음 commit에 넣을 파일을 staging한다.
- `git diff --cached --stat`: commit 직전 포함 파일과 변경량을 요약 확인한다.
- `git commit`: 로컬 이력으로 저장한다.
- `git branch -M main`: 현재 브랜치 이름을 `main`으로 바꾼다.

잘못 staging한 파일은 commit 전에 다음처럼 뺄 수 있다. 파일 자체는 삭제되지 않는다.

```powershell
git restore --staged "경로\파일명"
```

### 3-3. GitHub 웹에서 빈 repository 생성

1. GitHub 로그인 후 우측 상단 `+ → New repository`를 누른다.
2. Repository name: `semiconductor-packaging-engineering-portfolio`
3. Description을 입력한다.
4. 처음에는 Public 또는 검토용 Private을 선택한다.
5. **Add a README file, Add .gitignore, Choose a license를 모두 선택하지 않는다.** 로컬에 이미 파일과 이력이 있기 때문이다.
6. `Create repository`를 누른다.

License는 사용자가 코드 재사용 조건을 정할 때 별도로 선택한다. 지금은 의도 없이 자동 추가하지 않아도 된다.

### 3-4. 로컬과 GitHub 연결 후 push

GitHub가 보여 주는 HTTPS URL을 복사한다.

```powershell
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/semiconductor-packaging-engineering-portfolio.git
git remote -v
git push -u origin main
```

- `origin`: GitHub 원격 저장소의 관례적 별명이다.
- `-u`: 이후에는 `git push`만 입력해도 `origin/main`을 기본 대상으로 사용하게 한다.
- GitHub 계정 비밀번호를 터미널에 직접 입력하는 방식은 사용하지 않는다. Windows의 브라우저 로그인/Git Credential Manager가 나타나면 계정 인증을 진행한다.

원격 URL을 잘못 입력했다면 삭제/재생성보다 다음처럼 고친다.

```powershell
git remote set-url origin https://github.com/YOUR_GITHUB_USERNAME/정확한저장소명.git
```

### 3-5. 평소 사용하는 5단계

```powershell
git status
git diff
git add "수정한파일경로"
git commit -m "변경 이유를 설명하는 메시지"
git push
```

폴더 전체를 무조건 `git add .` 하기보다 처음에는 파일 경로를 명시하고 `git status`로 확인하는 습관을 권장한다.

## 4. 업로드 후 GitHub 웹에서 확인할 것

1. 저장소 첫 화면에서 루트 `README.md`가 정상 렌더링되는가?
2. Root-cause, robust-window, confirmation SVG 그림이 보이는가?
3. A3, notebook, literature, interview 링크가 열리는가?
4. 실제 개인정보·비밀·회사 데이터가 없는가?
5. Projects 2–6이 `Planned`로 표시되어 완료 실적으로 오해되지 않는가?
6. 저장소 `About` 영역에 description과 topic을 설정했는가?

추천 topics:

`semiconductor-packaging`, `process-engineering`, `compression-molding`, `doe`, `msa`, `mechanical-engineering`, `synthetic-data`

GitHub README에서는 현재 사용한 `project_01_molding/figures/...` 같은 상대경로가 branch/fork에서도 잘 동작한다.

## 5. 자주 생기는 문제

### `Author identity unknown`

`git config user.name`과 `git config user.email`이 설정되지 않은 상태다. 3-1을 수행한다.

### `remote origin already exists`

이미 origin이 있다. 먼저 확인한다.

```powershell
git remote -v
```

주소만 틀렸다면 `git remote set-url origin ...`으로 수정한다.

### Push가 인증에서 막힘

비밀번호를 반복 입력하지 않는다. GitHub Desktop에 로그인해 publish하거나, 설치된 Git Credential Manager의 브라우저 인증을 사용한다.

### GitHub에 그림이 안 보임

README의 이미지 경로 대소문자와 파일 위치를 확인한다. Windows는 대소문자 차이를 숨길 수 있지만 GitHub 서버에서는 문제가 될 수 있다.

### Notebook이 너무 크거나 렌더링이 느림

출력을 정리하고 notebook을 다시 저장한다. 단일 파일이 GitHub 일반 제한을 넘지 않는지 확인한다. 이 프로젝트의 핵심 결론은 README/A3에도 남겨 notebook 렌더링에만 의존하지 않는다.

### Windows에서 `python.exe`가 Microsoft Store로 연결되거나 실행되지 않음

`python --version`을 먼저 확인한다. Store 별칭만 열리거나 접근 오류가 나면 [Python 공식 배포판](https://www.python.org/downloads/windows/)을 설치하면서 `Add python.exe to PATH`를 선택하거나, Windows `설정 → 앱 → 고급 앱 설정 → 앱 실행 별칭`에서 불필요한 Store Python 별칭을 끈다. 설치 후 새 PowerShell을 열고 다시 확인한다.

```powershell
python --version
python -m pip --version
```

## 6. 하지 말아야 할 것

- access token, 비밀번호, `.env`를 commit하지 않는다.
- 처음부터 `git push --force`를 사용하지 않는다.
- 인터넷에서 찾은 다른 사람의 repository를 출처 없이 복사하지 않는다.
- 실제 Fab 결과처럼 제목이나 성과 수치를 과장하지 않는다.
- 문제가 생겼다고 `git reset --hard`를 먼저 실행하지 않는다. 작업이 삭제될 수 있다.

## 7. 공식 도움말

- [로컬 저장소를 GitHub에 추가하기](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
- [Git 설정 시작하기](https://docs.github.com/en/get-started/git-basics/set-up-git)
- [Git username 설정](https://docs.github.com/en/get-started/git-basics/setting-your-username-in-git)
- [README 소개](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [GitHub Markdown 문법](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
- [GitHub Desktop에 저장소 추가·복제](https://docs.github.com/en/desktop/adding-and-cloning-repositories)
