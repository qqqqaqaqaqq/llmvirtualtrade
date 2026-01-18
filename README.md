# Prompt 기반 LLM Virtual Trade Backtesting
---

## 해당 프로그램은 실제 트레이딩 전 백테스팅용 프로그램입니다.
> ⚠️ **Warning**  
> LLM API 호출 비용이 발생합니다.
<br>
## This is a backtesting program designed to evaluate trading strategies before deploying them in real trades.
> ⚠️ **Warning**  
> LLM API usage will incur costs.
---

## Process 
![Flow Chart](./images/flow.png)
- 마켓 데이터와 전략으로 LLM이 얼마만큼 수익을 낼 수 있는지 테스트 하기위한 백테스팅 프로그램 입니다.
- 마켓 데이터 지원 목록은 indicators.py 파일 확인 부탁드립니다.
<br>
- This is a backtesting application used to evaluate the profitability of LLM-driven trading strategies based on market data.
- The list of supported market data indicators can be found in the `indicators.py` file.
---

### Support Model
- LLM API Model : GPT-5.0-mini and Gemini 3.0 Flash / 2.5 Pro
### Required Software
- Databse : Postgres
### Market Data API
- Exchange : Upbit
### Runtime Environment
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

- **fail**
![Fail image](./images/failimage.png)

- **success**
![Success image](./images/successimage.png)
- If the process succeeds, a `.env` file and a `logs` folder will be generated.





