# Prompt 기반 LLM Virtual Trade Backtesting
---

- 해당 프로그램은 실제 트레이딩 전 백테스팅용 프로그램입니다.
> ⚠️ **Warning**  
> LLM API 호출 비용이 발생합니다.

- This is a backtesting program designed to evaluate trading strategies before deploying them in real trades.
> ⚠️ **Warning**  
> LLM API usage will incur costs.
---

## Process 
![Flow Chart](./images/flow.png)
- 마켓 데이터와 전략으로 LLM이 얼마만큼 수익을 낼 수 있는지 테스트 하기위한 백테스팅 프로그램 입니다.
- 마켓 데이터 지원 목록은 indicators.py 파일 확인 부탁드립니다.

- This is a backtesting application used to evaluate the profitability of LLM-driven trading strategies based on market data.
- The list of supported market data indicators can be found in the `indicators.py` file.
---

## 지원 되는 모델
- LLM API Model : GPT-5.0-mini and Gemini 3.0 Flash / 2.5 Pro
## 필수 설치 프로그램
- Databse : Postgres
## 마켓 데이터 API
- Exchange : Upbit
## 실행 환경
- Windows 11
---

## FORM
- **init form**
- ![DataBase input](./images/DBINPUT.png)
- **DB_HOST**: Database host (e.g., `localhost`)
- **DB_USER**: PostgreSQL username (e.g., `postgres`)
- **DB_PASSWORD**: PostgreSQL user password
- **DB_NAME**: Your database name
- **DB_PORT**: Database port (e.g., `5432`)

- **fail image**
- ![Fail image](./images/failimage.png)

- **success image**
- ![Success image](./images/successimage.png)
- 성공시 파일 내 .env 파일과 logs 폴더가 생성됩니다.




