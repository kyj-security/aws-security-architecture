# AWS 기반 클라우드 보안 아키텍처 설계 · 구축 · 진단 프로젝트

## 프로젝트 목표

AWS 환경에서 네트워크 분리, IAM 최소권한, 자동 취약점 진단, 로깅/모니터링까지 실무 수준의 보안 설계 사이클을 직접 설계·구축·검증하며, 그 과정을 포트폴리오로 정리한다.

## 왜 이 아키텍처인가

- **Public/Private 서브넷 분리**: 외부에 직접 노출되는 리소스(Bastion Host)와 보호가 필요한 리소스(웹서버)를 물리적으로 분리하여 공격 표면을 최소화
- **Bastion Host를 통한 단일 접근 경로**: 프라이빗 서브넷에 대한 SSH 접근을 Bastion 한 곳으로만 제한하여, 접근 경로를 단순화하고 감시 지점을 명확히 함
- **NAT Gateway를 통한 아웃바운드 전용 경로**: 프라이빗 서브넷의 리소스는 인터넷에서 직접 접근이 불가능하고, 나가는 트래픽만 NAT Gateway를 거치도록 구성

## 아키텍처 구성

![아키텍처 다이어그램](./architecture-diagram.png)

| 구성 요소 | 설명 |
|---|---|
| VPC | 10.0.0.0/16 (aws-security-lab-vpc) |
| Public Subnet A / C | 10.0.1.0/24, 10.0.2.0/24 — Bastion Host, NAT Gateway 위치 |
| Private Subnet A / C | 10.0.11.0/24, 10.0.12.0/24 — 웹서버(EC2) 위치 |
| Internet Gateway | Public Subnet의 인터넷 인바운드/아웃바운드 경로 |
| NAT Gateway | Private Subnet의 아웃바운드 전용 경로 (public-subnet-a에 위치) |
| Bastion Host | 프라이빗 리소스 접근을 위한 유일한 SSH 진입점 (4단계에서 배포) |

## 2단계: VPC & 네트워크 인프라 구축 결과

리전: Asia Pacific (Seoul, ap-northeast-2)

| 리소스 | 이름 | 세부 내용 |
|---|---|---|
| VPC | aws-security-lab-vpc | 10.0.0.0/16 |
| Subnet | public-subnet-a | 10.0.1.0/24, ap-northeast-2a |
| Subnet | public-subnet-c | 10.0.2.0/24, ap-northeast-2c |
| Subnet | private-subnet-a | 10.0.11.0/24, ap-northeast-2a |
| Subnet | private-subnet-c | 10.0.12.0/24, ap-northeast-2c |
| Internet Gateway | aws-security-lab-igw | VPC에 연결(Attached) 완료 |
| NAT Gateway | aws-security-lab-nat | public-subnet-a에 위치, Elastic IP 자동 할당 |
| Route Table | public-rt | 0.0.0.0/0 → Internet Gateway, Public 서브넷 2개 연결 |
| Route Table | private-rt | 0.0.0.0/0 → NAT Gateway, Private 서브넷 2개 연결 |

## 3단계: IAM 설계 & 최소권한 적용 결과

### 역할(Role) 설계

| 역할 | 용도 | 연결 정책 |
|---|---|---|
| Admin-Role | 관리자용 | AdministratorAccess |
| App-Role | EC2 애플리케이션용 | AmazonS3ReadOnlyAccess + (아래 Before/After 참고) |
| ReadOnly-Role | 읽기 전용 | ReadOnlyAccess |

### Before / After 비교 (App-Role)

의도적으로 과도한 권한을 가진 정책을 App-Role에 부여한 뒤, 진단하고 최소권한으로 수정하는 과정을 기록했다.

**Before: `Overpermissive-Policy-BEFORE`**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```
→ 모든 AWS 서비스, 모든 리소스에 대한 전체 권한. 실무에서 흔히 발생하는 과도한 권한 부여 사례를 재현.

**After: `App-Role-LeastPrivilege-AFTER`**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowSpecificS3BucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::aws-security-lab-app-bucket/*"
    }
  ]
}
```
→ 실제 애플리케이션 동작에 필요한 특정 S3 버킷의 읽기/쓰기 권한으로 범위를 좁힘.

### 진단 방법

- IAM Access Analyzer의 **Unused access (Principal analysis)** 분석기를 생성하여, App-Role에 연결된 과도한 권한 중 실제로 사용되지 않은 권한을 탐지하도록 구성
- (진단 결과는 분석기 스캔 완료 후 추가 예정)

## 진행 단계

1. **준비 & 설계** ✅
2. **VPC & 네트워크 인프라 구축** ✅
3. **IAM 설계 & 최소권한 적용** ✅ (Unused Access 진단 결과 추가 예정)
4. 보안그룹/NACL 구성 및 EC2 배포 (Bastion Host, 웹서버 포함) ← 현재 위치
5. 자동 진단 & 검증 (Prowler / ScoutSuite)
6. 로깅/모니터링 (CloudTrail, GuardDuty, Wazuh)

## 사용 기술 / 도구

- AWS (VPC, EC2, IAM, CloudTrail, GuardDuty 등)
- draw.io (아키텍처 다이어그램)
- Prowler, ScoutSuite (보안 진단)
- Wazuh (SIEM / 로그 모니터링)
- Git, GitHub

## 진행 상황

- [x] 0단계: AWS 계정 준비, 로컬 개발환경 구성
- [x] 1단계: 아키텍처 다이어그램 및 README 작성
- [x] 2단계: VPC & 네트워크 인프라 구축
- [x] 3단계: IAM 최소권한 적용
- [ ] 4단계: 보안그룹/NACL 및 EC2 배포
- [ ] 5단계: 자동 진단 및 검증
- [ ] 6단계: 로깅/모니터링 구축
