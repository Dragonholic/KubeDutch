# 🍓 Raspberry Pi Deployment Guide

라즈베리 파이 4 또는 5 (RAM 4GB 이상 권장)에서 KubeDutch 시스템을 구동하기 위한 가이드입니다.

## 1. 필수 준비물 (Prerequisites)
- **H/W**: Raspberry Pi 4/5 (4GB/8GB RAM)
- **OS**: Raspberry Pi OS Lite (**64-bit**) 
  - *주의: 32-bit OS에서는 마인크래프트 서버가 제대로 메모리를 할당받지 못할 수 있습니다.*
- **Storage**: 고속 SD카드 또는 USB 3.0 SSD (로그 쓰기 속도 및 수명 때문)

## 2. 경량 Kubernetes (K3s) 설치
Minikube는 라즈베리 파이에서 너무 무겁습니다. IoT용 표준인 **K3s**를 사용합니다.

```bash
# 1. K3s 설치 (마스터 노드)
curl -sfL https://get.k3s.io | sh -

# 2. 권한 설정 (kubectl 사용을 위해)
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config

# 3. 상태 확인
kubectl get nodes
```

## 3. 소스 코드 복사 및 이미지 빌드 (ARM64)
PC(Windows)에서 빌드한 이미지는 파이에서 실행되지 않습니다. 파이에서 직접 빌드하는 것이 가장 확실합니다.

1. 이 프로젝트 폴더 전체를 라즈베리 파이로 복사합니다 (git clone 또는 scp 이용).
2. 파이 내부에서 도커 이미지를 빌드합니다.

```bash
# K3s는 자체 containerd를 사용하므로, 이미지를 K3s가 인식하게 하려면 
# 로컬 레지스트리를 쓰거나 Docker Hub에 올렸다 받아야 합니다.
# 가장 쉬운 방법: Docker Hub 사용

# 1. Docker 설치 (이미 설치되어 있다면 패스)
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 2. 로그인 (Docker Hub 계정 필요)
docker login

# 3. Multi-arch 빌드 및 푸시 (username을 본인 ID로 변경)
cd parser
docker build -t <your-docker-id>/kubedutch-parser:latest .
docker push <your-docker-id>/kubedutch-parser:latest
```

## 4. 설정 파일 수정
라즈베리 파이의 제한된 자원(RAM)에 맞춰 `k8s/minecraft-deployment.yaml`을 수정해야 합니다.

1. **이미지 주소 변경**: `image: kubedutch-parser:latest` -> `image: <your-docker-id>/kubedutch-parser:latest`
2. **리소스 제한 완화**:
   라즈베리 파이 4GB 모델인 경우, 4Gi 메모리 할당은 OS를 죽게 만들 수 있습니다.

```yaml
          resources:
            requests:
              memory: "1Gi"
              cpu: "500m"
            limits:
              memory: "2.5Gi" # 4GB 모델 기준 안전선
              cpu: "2000m"
```

## 5. 배포 및 실행

```bash
# Secret 생성 (Sepolia 키 설정)
kubectl create secret generic minecraft-secret \
  --from-literal=RPC_URL="https://rpc.sepolia.org" \
  --from-literal=PRIVATE_KEY="0x..." \
  --from-literal=CONTRACT_ADDRESS="0x..."

# 배포 적용
kubectl apply -f k8s/

# 로그 확인
kubectl get pods -w
```

## 6. 성능 최적화 팁 (Optional)
라즈베리 파이 CPU 부하를 줄이기 위해 마인크래프트 서버 옵션을 조정하세요.
`k8s/minecraft-deployment.yaml`의 `env` 섹션에 추가:

```yaml
            - name: VIEW_DISTANCE
              value: "6" # 시야 거리를 줄여 CPU 부하 감소
            - name: MAX_TICK_TIME
              value: "-1" # 렉 걸려도 서버 강제 종료 방지
```

