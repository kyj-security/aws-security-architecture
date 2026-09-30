# AWS 기반 클라우드 보안 아키텍처 설계 · 구축 · 진단 프로젝트

## 프로젝트 목표

AWS 환경에서 네트워크 분리, IAM 최소권한, 자동 취약점 진단, 로깅/모니터링까지 실무 수준의 보안 설계 사이클을 직접 설계·구축·검증하며, 그 과정을 포트폴리오로 정리한다.

## 왜 이 아키텍처인가

* **Public/Private 서브넷 분리**: 외부에 직접 노출되는 리소스(Bastion Host)와 보호가 필요한 리소스(웹서버)를 물리적으로 분리하여 공격 표면을 최소화
* **Bastion Host를 통한 단일 접근 경로**: 프라이빗 서브넷에 대한 SSH 접근을 Bastion 한 곳으로만 제한하여, 접근 경로를 단순화하고 감시 지점을 명확히 함
* **NAT Gateway를 통한 아웃바운드 전용 경로**: 프라이빗 서브넷의 리소스는 인터넷에서 직접 접근이 불가능하고, 나가는 트래픽만 NAT Gateway를 거치도록 구성

## 아키텍처 구성

!\[아키텍처 다이어그램](./architecture-diagram.png)

|구성 요소|설명|
|-|-|
|VPC|10.0.0.0/16|
|Public Subnet A / C|10.0.1.0/24, 10.0.2.0/24 — Bastion Host, NAT Gateway 위치|
|Private Subnet A / C|10.0.11.0/24, 10.0.12.0/24 — 웹서버(EC2) 위치|
|Internet Gateway|Public Subnet의 인터넷 인바운드/아웃바운드 경로|
|NAT Gateway|Private Subnet의 아웃바운드 전용 경로|
|Bastion Host|프라이빗 리소스 접근을 위한 유일한 SSH 진입점|

## 진행 단계

1. **준비 \& 설계** ← 현재 위치
2. VPC \& 네트워크 인프라 구축
3. IAM 설계 \& 최소권한 적용
4. 보안그룹/NACL 구성 및 EC2 배포
5. 자동 진단 \& 검증 (Prowler / ScoutSuite)
6. 로깅/모니터링 (CloudTrail, GuardDuty, Wazuh)

## 사용 기술 / 도구

* AWS (VPC, EC2, IAM, CloudTrail, GuardDuty 등)
* draw.io (아키텍처 다이어그램)
* Prowler, ScoutSuite (보안 진단)
* Wazuh (SIEM / 로그 모니터링)
* Git, GitHub

## 진행 상황

* \[x] 0단계: AWS 계정 준비, 로컬 개발환경 구성
* \[x] 1단계: 아키텍처 다이어그램 및 README 작성
* \[ ] 2단계: VPC \& 네트워크 인프라 구축
* \[ ] 3단계: IAM 최소권한 적용
* \[ ] 4단계: 보안그룹/NACL 및 EC2 배포
* \[ ] 5단계: 자동 진단 및 검증
* \[ ] 6단계: 로깅/모니터링 구축

