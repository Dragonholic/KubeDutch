# 🛰️ KubeDutch: Satellite Cluster Resource Ledger PoC
> **"조작 불가능한 위성 클러스터 자원 정산 시스템을 위한 지상 검증 모델"**
>
> **Ground Proof-of-Concept for Immutable Satellite Resource Auditing System**

## 📖 Project Motivation (연구 배경)
분산 시스템(Distributed Systems), 특히 **위성 클러스터(Satellite Cluster)** 환경에서는 다수의 위성이 협업하여 임무를 수행합니다. 이때 각 노드의 자원(CPU, 통신 대역폭 등) 사용량을 **위변조 불가능(Immutable)하고 투명하게(Transparent)** 기록하여 정산하는 것은 신뢰성 확보에 필수적입니다.

본 프로젝트는 이러한 위성 환경을 지상에서 모사하기 위해, **마인크래프트 게임 워크로드**를 위성 임무로 가정하고, **이더리움 블록체인**을 활용하여 신뢰할 수 있는 자원 사용 원장(Ledger)을 구축하는 실험적 연구입니다.

## 🏗 Architecture (시스템 구조)

위성 환경의 하드웨어 제약과 이기종성(Heterogeneity)을 반영하여 **하이브리드 분산 아키텍처**를 설계했습니다.

1.  **Mission Node (임무 위성) 🖥️**:
    *   **Role**: 고부하 워크로드 수행
    *   **Simulated by**: High-Performance PC
    *   **Workload**: Minecraft Server (CPU/RAM Intensive)
    *   **Agent**: Log Sender (Telemetry Transmission)

2.  **Telemetry Node (관제 위성) 🍓**:
    *   **Role**: 로그 수집, 검증 및 온체인 기록
    *   **Simulated by**: Raspberry Pi 4 (Edge Device)
    *   **System**: Lightweight Kubernetes (K3s)
    *   **Service**: Log Parser API, Web Dashboard

3.  **Immutable Ledger (불변 장부) 🔗**:
    *   **Role**: 영구적이고 위변조 불가능한 데이터 저장
    *   **Network**: Ethereum Sepolia Testnet
    *   **Smart Contract**: `UsageLedger.sol`

## 🚀 Key Features
- **Data Integrity**: 블록체인 기술을 도입하여 관리자조차 로그를 임의로 수정할 수 없음.
- **Edge Computing**: 기록 부하를 임무 노드에서 분리하여 전체 시스템 성능 최적화.
- **Standardization**: EVM 표준 및 Standard Kubernetes API 준수.

## 🛠 Tech Stack
- **Infra**: Kubernetes (K3s), Docker
- **Blockchain**: Solidity, Ethereum Sepolia, Ethers.js
- **Backend**: Python (FastAPI, Web3.py)
- **Frontend**: React (Vite)
- **Simulation**: Minecraft Java Edition

## 🚀 Quick Start
자세한 실행 방법은 [STEP_BY_STEP.md](STEP_BY_STEP.md) 및 [RASPBERRY_PI_GUIDE.md](docs/RASPBERRY_PI_GUIDE.md)를 참고하세요.
