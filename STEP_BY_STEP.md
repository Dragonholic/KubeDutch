# 🔰 왕초보를 위한 KubeDutch 따라하기 가이드

이 문서는 **"지금 당장 뭐부터 해야 해?"** 라고 묻는 분들을 위한 **100% 실전 가이드**입니다.
순서대로 하나씩 체크(✅)하면서 진행해 보세요.

---

## 1️⃣ 1단계: 블록체인 지갑 준비하기 (PC)

블록체인 장부를 쓰려면 '관리자 도장'이 필요합니다. 그게 바로 **지갑(Private Key)**입니다.

1.  [MetaMask(메타마스크)](https://metamask.io/) 크롬 확장프로그램을 설치하고 가입하세요.
2.  메타마스크 왼쪽 위 네트워크 선택 버튼을 누르고 **'Show/hide test networks'**를 켠 뒤, **Sepolia**를 선택하세요.
3.  **[Sepolia Faucet(수도꼭지)](https://sepoliafaucet.com/)** 사이트에 가서 내 지갑 주소를 넣고 **"Send Me ETH"**를 누르세요. (가짜 돈 받기)
4.  메타마스크에 `0.5 SepoliaETH` 정도가 들어왔는지 확인하세요.
5.  **[Remix IDE](https://remix.ethereum.org/)**에 접속해서 스마트 컨트랙트를 배포합니다. (아래 상세 설명 필독!)

### 🛠️ Remix IDE 상세 배포 가이드 (중요)

1.  **파일 만들기**:
    *   Remix 왼쪽 메뉴의 **File Explorers** (문서 아이콘)를 클릭합니다.
    *   `contracts` 폴더 안에 새 파일 만들기 버튼을 누르고 이름을 `UsageLedger.sol`로 짓습니다.
    *   우리가 작성한 `contracts/UsageLedger.sol` 코드 전체를 복사해서 붙여넣습니다.

2.  **컴파일 (기계어 변환)**:
    *   왼쪽 메뉴의 **Solidity Compiler** (S자 모양 아이콘)를 클릭합니다.
    *   파란색 **"Compile UsageLedger.sol"** 버튼을 클릭합니다.
    *   버튼 왼쪽에 초록색 체크 표시(✅)가 뜨면 성공!

3.  **배포 (블록체인 등록)**:
    *   왼쪽 메뉴의 **Deploy & Run Transactions** (이더리움 로고 아이콘)를 클릭합니다.
    *   맨 위 **ENVIRONMENT**를 클릭하고 **"Injected Provider - MetaMask"**를 선택합니다. (메타마스크 창이 뜨면 승인하세요)
    *   **ACCOUNT**에 내 메타마스크 지갑 주소가 떴는지 확인합니다. (Sepolia 네트워크인지도 확인!)
    *   주황색 **"Deploy"** 버튼을 클릭합니다.
    *   메타마스크 팝업이 뜨면 **"확인(Confirm)"**을 눌러 가스비를 냅니다.

4.  **정보 가져오기**:
    *   하단 **Deployed Contracts** 섹션에 `UsageLedger`가 생겼을 겁니다.
    *   이름 옆의 **복사 아이콘(📄)**을 눌러서 **`Contract Address`**를 복사해두세요. (예: `0x1234...`)
    - 
    *   이 주소가 바로 2단계(라즈베리 파이 설정)에서 필요한 주소입니다.

    *   👉 **여기서 얻어야 할 것 2가지 (메모장 필수!)**:
        1.  `Contract Address`: 방금 복사한 주소
        2.  `Private Key`: 내 메타마스크 지갑의 비밀키 (메타마스크 우상단 점3개 -> 계정 세부 정보 -> 비공개 키 표시)


---

## 2️⃣ 2단계: 라즈베리 파이 세팅하기 (매니저 준비)

라즈베리 파이를 **"24시간 일하는 매니저"**로 만드는 과정입니다. 라즈베리 파이 터미널을 켜세요.

### 1. 소스코드 가져오기
```bash
git clone <내_깃허브_주소>
cd KubeDutch
```

### 2. API 서버 이미지 만들기
```bash
cd parser
docker build -t kubedutch-api:latest .
# (시간이 좀 걸립니다. 3B 모델이라면 5~10분 정도?)
cd ..
```

### 3. 매니저(서버) 실행하기 (Docker Native)
라즈베리 파이 3B의 성능을 고려하여 가벼운 Docker로 직접 실행합니다.
(아래 명령어의 `0x...` 부분을 본인 지갑 정보로 바꿔서 **한 줄씩 복사해서** 실행하세요!)

```bash
# 1. 기존 컨테이너가 있다면 삭제 (깨끗하게 시작)
sudo docker rm -f kubedutch-api

# 2. 서버 실행 (백그라운드 모드)
sudo docker run -d --restart=always \
  -p 8000:8000 \
  -e RPC_URL="https://rpc.sepolia.org" \
  -e PRIVATE_KEY="0x내_지갑_비밀키" \
  -e CONTRACT_ADDRESS="0x아까_만든_컨트랙트_주소" \
  --name kubedutch-api \
  kubedutch-api:latest
```
*   `sudo docker ps`를 쳤을 때 `kubedutch-api`가 보이면 성공!
*   `hostname -I`를 쳐서 **라즈베리 파이 IP 주소**를 메모해두세요.

### 4. 웹 사이트 켜기
```bash
cd web
npm install
npm run dev -- --host 0.0.0.0 &
```

---

## 3️⃣ 3단계: PC 세팅하기 (게임기 준비)

이제 고성능 PC로 돌아오세요.

### 1. 마인크래프트 서버 켜기
*   다운받은 `paper.jar`를 실행해서 서버를 켭니다. (`start.bat`)
*   검은색 창에 서버가 켜지고 로그가 막 올라오면 성공!

### 2. 연결 프로그램(Sender) 설정하기
*   프로젝트 폴더의 `parser/sender.py` 파일을 메모장이나 VSCode로 엽니다.
*   아까 메모한 **라즈베리 파이 IP**와 **내 컴퓨터 로그 경로**를 적어줍니다.

```python
# 예시
RASPBERRY_PI_IP = "192.168.0.15" 
LOG_FILE_PATH = r"C:\Minecraft\logs\latest.log"
```

### 3. 연결 프로그램 실행
```powershell
# PC 터미널에서
python parser/sender.py
```
*   `📤 Log Sender Started` 라고 뜨면 준비 끝!

---

## 4️⃣ 4단계: 최종 테스트 (두근두근)

이제 모든 시스템이 연결되었습니다.

1.  **마인크래프트 접속**: 게임을 켜고 `Multiplayer` -> `localhost`로 접속하세요.
2.  **게임 플레이**: 10초 정도 점프하고 돌아다니세요.
3.  **접속 종료**: `Disconnect`를 눌러 나갑니다.
4.  **확인**:
    *   PC 터미널(`sender.py`)에: **"✅ Sent Success"** 라고 떴나요?
    *   라즈베리 파이 웹사이트(`http://라즈베리파이IP:8080`)에 들어가서 **Refresh**를 눌러보세요.
    *   방금 내가 게임한 시간이 **표**에 떴나요?

🎉 **축하합니다! 블록체인 기반 더치페이 시스템 구축에 성공하셨습니다!**

