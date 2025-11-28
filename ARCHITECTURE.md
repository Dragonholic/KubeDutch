# 🛰️ System Architecture: Satellite Cluster PoC

본 문서는 **위성 클러스터 환경**에서의 자원 사용 로그 기록 및 정산을 위한 **지상 검증 시스템(Ground PoC)**의 아키텍처를 설명합니다.

---

## 1. Design Philosophy (설계 철학)

위성 네트워크와 같은 **극한의 엣지 환경(Extreme Edge)**에서는 다음과 같은 제약 사항이 존재합니다.

1.  **자원 제약**: 모든 위성이 블록체인 풀 노드를 돌릴 수 없음.
2.  **신뢰 문제**: 데이터가 지상국에 도달하기 전, 중간 노드에서 변조될 위험이 있음.
3.  **부하 분리**: 핵심 임무(Mission)를 수행하는 도중에 로그 기록으로 인해 성능이 저하되면 안 됨.

따라서 본 프로젝트는 **"임무 수행(Mission)"과 "기록 관리(Audit)"를 물리적으로 분리**하는 **Two-Tier Architecture**를 채택했습니다.

---

## 2. Architecture Diagram

```mermaid
graph LR
    subgraph Mission_Segment [🛰️ Mission Satellite (PC)]
        Core[🚀 Mission Workload]
        Note1[Simulation: Minecraft Server]
        Sender[📡 Telemetry Agent]
    end

    subgraph Telemetry_Segment [🛰️ Audit Satellite (Raspberry Pi)]
        K8s[☸️ Edge Kubernetes]
        API[📝 Ledger Oracle]
        Web[📊 Ground Station Dashboard]
    end

    subgraph Blockchain_Layer [🌍 Immutable Ledger]
        Eth[🔗 Ethereum Sepolia]
        Contract[📜 Smart Contract]
    end

    Core -- Resource Usage Logs --> Sender
    Sender -- Telemetry Data (HTTP/TCP) --> API
    API -- Signed Transaction --> Eth
    Eth -- Event Logs --> Web
    Web -- Visualization --> User[👨‍🚀 Operator]
```

---

## 3. Component Details

### 🛰️ Mission Node (High-Performance PC)
실제 위성 환경의 **Payload(탑재체)** 역할을 담당합니다.
- **Minecraft Server**: CPU/Memory 자원을 많이 소모하는 실제 임무(Mission)를 모사합니다.
- **Log Sender**: 생성된 로그를 실시간으로 감지하여 최소한의 오버헤드로 Audit Node로 전송합니다. (Python, Lightweight)

### 🛰️ Audit Node (Raspberry Pi 4)
위성 클러스터 내의 **Gateway** 또는 **Controller** 역할을 담당합니다.
- **K3s (Lightweight K8s)**: 자원이 제한된 엣지 환경에서의 컨테이너 오케스트레이션을 검증합니다.
- **API Server (Ledger Oracle)**: 수신된 데이터를 검증하고, 관리자 개인키(Private Key)로 서명하여 블록체인 네트워크로 전파합니다.

### 🌍 Blockchain Layer (Ethereum Sepolia)
**지상국(Ground Station)의 신뢰할 수 있는 원장** 역할을 합니다.
- **Smart Contract**: 자원 사용량(Duration)과 비용(Cost)을 기록하며, 오직 인증된 Audit Node(Owner)만이 기록 권한을 가집니다.
- **Immutability**: 한 번 기록된 로그는 위성이나 해커가 임의로 삭제할 수 없습니다.

---

## 4. Scenario Flow (검증 시나리오)

1.  **Mission Start**: 임무 위성(PC)에서 워크로드(게임)가 시작됩니다.
2.  **Activity**: 사용자가 자원을 점유하며 활동합니다.
3.  **Mission End**: 워크로드가 종료되면, `Log Sender`가 즉시 사용량(Duration)을 계산하여 전송합니다.
4.  **Verification**: 감시 위성(Raspberry Pi)이 데이터 형식을 검증합니다.
5.  **Finalize**: 검증된 데이터가 이더리움 블록체인에 트랜잭션으로 기록되어 **영구적(Permanent)** 상태가 됩니다.
6.  **Audit**: 지상 운영자는 대시보드를 통해 투명하게 공개된 자원 사용 내역을 확인합니다.
