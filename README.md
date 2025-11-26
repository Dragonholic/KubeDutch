# KubeDutch: Kubernetes Minecraft Ledger

Standard Kubernetes 환경에서 마인크래프트 서버를 운영하고, 사용자 접속 기록을 이더리움 세폴리아(Sepolia) 블록체인에 투명하게 기록하는 시스템입니다.

## 🏗 Architecture

1. **Infrastructure**: Kubernetes (Deployment, PVC, Service)
2. **Server**: Minecraft Java Edition (PaperMC)
3. **Agent**: Python Sidecar Container (Log Parser -> Web3.py -> Ethereum)
4. **Blockchain**: Ethereum Sepolia Testnet (Solidity Smart Contract)
5. **Frontend**: React Dashboard (Ethers.js)

## 🚀 Prerequisite

- Kubernetes Cluster (Minikube, Kind, or Cloud)
- Python 3.9+
- Node.js 18+
- Ethereum Wallet (MetaMask) with Sepolia ETH

## 🛠 Installation & Deployment

### 1. Smart Contract Deployment
1. `contracts/UsageLedger.sol`을 Remix IDE(https://remix.ethereum.org)에 복사합니다.
2. Injected Provider (MetaMask)를 선택하고 Sepolia 네트워크에 배포합니다.
3. 배포된 **Contract Address**를 복사해둡니다.

### 2. Configuration
루트 디렉토리에 `.env` 파일을 생성하고 다음 정보를 입력합니다. (보안 주의)

```env
# Blockchain Config
RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE
CONTRACT_ADDRESS=0xDEPLOYED_CONTRACT_ADDRESS

# Dashboard Config (Optional)
VITE_CONTRACT_ADDRESS=0xDEPLOYED_CONTRACT_ADDRESS
```

### 3. Build & Deploy Agent (Docker & K8s)
K8s 클러스터가 로컬 이미지를 사용할 수 있도록 설정하거나, Docker Hub에 이미지를 푸시해야 합니다.

```bash
# Docker Image 빌드
docker build -t kubedutch-parser:latest ./parser

# (Minikube 사용 시)
minikube image load kubedutch-parser:latest

# Kubernetes 배포
kubectl apply -f k8s/minecraft-pvc.yaml
kubectl apply -f k8s/minecraft-deployment.yaml # image: kubedutch-parser:latest 확인 필요
kubectl apply -f k8s/minecraft-service.yaml
```

### 4. Run Dashboard (Web)
```bash
cd web
npm install

# src/App.jsx 내의 CONTRACT_ADDRESS 변수를 배포한 주소로 변경하세요.
npm run dev
```

이제 브라우저에서 `http://localhost:8080`으로 접속하여 대시보드를 확인합니다.

## 🧪 Testing
1. 마인크래프트 클라이언트로 `localhost:30001`에 접속합니다.
2. 게임에 접속했다가 로그아웃합니다.
3. `parser` 컨테이너 로그를 확인합니다: `kubectl logs -f deployment/minecraft-server -c log-parser`
4. 트랜잭션이 성공하면, 웹 대시보드에서 새로고침하여 기록을 확인합니다.
