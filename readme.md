# 파이썬 프로그래밍

## 가상환경

### 1. 가상환경 생성

```bash
python -m venv venv
```

### 2. 가상환경 활성화

```bash
#  Windows
.\venv\Scripts\Activate

# macOS/Linux
source venv/bin/activate

# 가상환경 비활성화
deactivate
```

### 3. 주피터 노트북 관련 모듈 설치

```bash
pip install -r requirements.txt
```

### 4. 가상환경을 주피터 노트북 커널로 등록 (선택)
```bash
python -m ipykernel install --user --name skt-venv --display-name "Python(SKT venv)"
```