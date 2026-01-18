# Prompt 기반 LLM Virtual Trade Backtesting
---
## 해당 프로그램은 실제 트레이딩 전 백테스팅용 프로그램입니다.
## This is a backtesting program designed to evaluate trading strategies before deploying them in real trades.

> ⚠️ **Warning**  
> LLM API 호출 비용이 발생하오니 필히 인지하여 주세요.
---
## 메인 Process 
![Flow Chart](./images/flow.png)
- Market Data + Strategy => LLM Response Msg => Virtual Trade
- Support Market Data indicator => indicators.py
---
## 현재 지원되는 모델
- LLM API Model : GPT-5.0-mini and Gemini 3.0 Flash / 2.5 Pro
- Databse : Postgres
## 마켓 데이터 API
- Exchange : Upbit
---
## 실행 환경
- Windows 11
---
## FORM
- **init form**
![DataBase input](./images/DBINPUT.png)
- **DB_HOST**: Database host (e.g., `localhost`)
- **DB_USER**: PostgreSQL username (e.g., `postgres`)
- **DB_PASSWORD**: PostgreSQL user password
- **DB_NAME**: Your database name
- **DB_PORT**: Database port (e.g., `5432`)

- **fail image**
![Fail image](./images/failimage.png)

- **success image**
![Success image](./images/successimage.png)
and generated .env, logs/




