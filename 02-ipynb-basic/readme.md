# 주피터 노트북

## 주피터 노트북이란?

주피터 노트북(Jupyter Notebook)은 코드, 텍스트, 수식, 시각화를 하나의 문서에서 작성하고 실행할 수 있는 대화형 개발 환경 - 데이터 분석, 머신러닝, 과학 계산 분야에서 널리 사용.

## 주요 특징

- **대화형 실행**: 코드를 셀 단위로 작성하고 즉시 실행 가능
- **다양한 언어 지원**: Python, R, Julia 등 40개 이상의 언어 지원
- **시각화**: 그래프와 차트를 인라인으로 표시
- **문서화**: 마크다운을 사용한 설명 추가 가능

## VS Code에서 주피터 노트북 설정 방법

### 1. Python 확장 설치
- VS Code 확장 마켓플레이스에서 "Python" 검색 후 설치
- Microsoft에서 제공하는 공식 Python 확장 설치

### 2. Jupyter 확장 설치
- "Jupyter" 확장 검색 후 설치
- 또는 Python 확장 설치 시 자동으로 포함됨

### 3. Python 환경 설정
```bash
# pip를 통한 설치
pip install jupyter notebook ipykernel
```

### 4. 노트북 파일 생성 및 실행
1. `.ipynb` 확장자로 새 파일 생성
2. 커널 선택 (Select Kernel 버튼 클릭)
3. Python 인터프리터 선택
4. 셀에 코드 작성 후 `Shift + Enter`로 실행

### 5. 유용한 단축키
- `Shift + Enter`: 현재 셀 실행 후 다음 셀로 이동
- `Ctrl + Enter`: 현재 셀 실행
- `Alt + Enter`: 현재 셀 실행 후 아래에 새 셀 추가
- `A`: 위에 셀 추가
- `B`: 아래에 셀 추가
- `DD`: 셀 삭제
