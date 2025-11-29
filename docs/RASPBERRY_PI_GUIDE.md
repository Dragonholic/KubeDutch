# 🍓 Raspberry Pi Hybrid Guide

PC에서 고사양 마인크래프트 서버를 돌리고, 라즈베리 파이는 블록체인 기록만 담당하는 **하이브리드 구성 가이드**입니다.

## 🏛 구성도
- **PC (Windows)**: Minecraft Server + Log Sender (`parser/sender.py`)
- **Raspberry Pi**: K8s API Server (`k8s/pi-deployment.yaml`) + Web Dashboard

---

## 🟢 Part 1: 라즈베리 파이 설정 (받는 쪽)

### 1. 프로젝트 준비
```bash
git clone <REPO_URL>
cd KubeDutch
```

### 2. API 서버 이미지 빌드 (ARM64)
```bash
cd parser
# 라즈베리 파이 자체에서 빌드해야 합니다.
docker build -t kubedutch-api:latest .
```

### 3. Kubernetes 배포 (API 서버만)
> **Note:** 라즈베리 파이 3B 이하 모델에서는 K8s 대신 Docker 직접 실행을 권장합니다.

#### Option A: Docker 직접 실행 (추천 - 가벼움)
```bash
sudo docker run -d --restart=always \
  -p 8000:8000 \
  -e RPC_URL="https://rpc.sepolia.org" \
  -e PRIVATE_KEY="0xYOUR_PRIVATE_KEY" \
  -e CONTRACT_ADDRESS="0xYOUR_CONTRACT_ADDRESS" \
  --name kubedutch-api \
  kubedutch-api:latest
```

#### Option B: Kubernetes 배포 (고성능 모델용)
마인크래프트 서버를 제외한 가벼운 버전의 K8s 설정 파일입니다.
```bash
# 1. 비밀키 설정 (Sepolia 지갑 정보)
kubectl create secret generic minecraft-secret \
  --from-literal=RPC_URL="https://rpc.sepolia.org" \
  --from-literal=PRIVATE_KEY="0xYOUR_PRIVATE_KEY" \
  --from-literal=CONTRACT_ADDRESS="0xYOUR_CONTRACT_ADDRESS"

# 2. 배포
kubectl apply -f k8s/pi-deployment.yaml

# 3. IP 확인
hostname -I
# -> 나온 IP 주소를 PC 설정 때 사용합니다.
```

### 4. 웹 대시보드 실행
```bash
cd web
npm install
npm run dev -- --host 0.0.0.0
```

---

## 🔵 Part 2: PC 설정 (보내는 쪽)

### 1. 마인크래프트 서버 실행
[PaperMC](https://papermc.io) 등을 다운받아 평소처럼 실행합니다.

### 2. Log Sender 실행
마인크래프트 로그를 라즈베리 파이로 쏴주는 프로그램입니다.

1. `parser/sender.py` 파일을 엽니다.
2. 아래 두 가지를 수정합니다:
   ```python
   RASPBERRY_PI_IP = "192.168.0.XX"  # 라즈베리 파이 IP
   LOG_FILE_PATH = r"C:\Minecraft\logs\latest.log" # 마인크래프트 로그 경로
   ```
3. 실행:
   ```powershell
   pip install requests
   python parser/sender.py
   ```

### 3. 테스트
PC 마인크래프트에 접속했다가 나간 뒤, `sender.py` 화면에 **"✅ Sent Success"**가 뜨면 성공입니다!
