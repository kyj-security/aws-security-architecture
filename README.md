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
- [x] 4단계: 보안그룹/NACL 및 EC2 배포
- [ ] 5단계: 자동 진단 및 검증
- [ ] 6단계: 로깅/모니터링 구축

## Stage 4: 보안 그룹 / NACL / EC2 배포

### 구성 요약
- Bastion Host (public-subnet-a, 10.0.1.0/24): 내 IP에서 오는 SSH만 허용 (bastion-sg)
- Web Server (private-subnet-a, 10.0.11.0/24): 퍼블릭 IP 없음, bastion-sg에서 오는 SSH만 허용 (web-sg)
- private-nacl: private-subnet-a, private-subnet-c에 연결. public 서브넷은 기본 NACL 유지

### 보안 그룹
| 이름 | 인바운드 | 목적 |
|---|---|---|
| bastion-sg | SSH(22) / 내 IP | 관리자 진입점 |
| web-sg | SSH(22) / bastion-sg | bastion을 거친 접속만 허용 |

### private-nacl 규칙
인바운드
| 번호 | 프로토콜/포트 | 소스 | 동작 |
|---|---|---|---|
| 100 | TCP 22 | 10.0.1.0/24 | 허용 |
| 110 | TCP 1024-65535 | 0.0.0.0/0 | 허용 |
| * | 전체 | 0.0.0.0/0 | 거부 |

아웃바운드
| 번호 | 프로토콜/포트 | 대상 | 동작 |
|---|---|---|---|
| 100 | TCP 443 | 0.0.0.0/0 | 허용 |
| 110 | TCP 80 | 0.0.0.0/0 | 허용 |
| 120 | TCP 1024-65535 | 10.0.1.0/24 | 허용 |
| * | 전체 | 0.0.0.0/0 | 거부 |

### 검증 결과
1. bastion을 경유한 web-server SSH 접속: 성공
2. web-server에서 curl -I https://aws.amazon.com (NAT Gateway 경유): HTTP/2 200
3. 노트북에서 web-server 프라이빗 IP로 직접 SSH 시도: Connection timed out (차단 확인)

### 설계 포인트
- 심층 방어: 인스턴스 단위(보안 그룹)와 서브넷 단위(NACL)로 이중 통제
- NACL은 Stateless라서 SSH 응답과 외부 통신 응답용 임시 포트(1024-65535) 규칙을 별도로 열어야 함
- 개인 키를 bastion에 복사하지 않고 ProxyCommand(점프 호스트 방식)로 접속
- web-server는 퍼블릭 IP가 없고, 외부 통신은 NAT Gateway를 통해서만 나감

## Stage 5: 자동화 진단 (보안 그룹 점검 스크립트)

### 개요
콘솔에서 수동으로 구성한 보안 설정을 파이썬(boto3) 스크립트가 자동으로 점검한다.
점검 대상은 보안 그룹의 인바운드 규칙이며, SSH(22), RDP(3389), DB 포트(MySQL, PostgreSQL, MSSQL, Redis, MongoDB)나 모든 포트가 0.0.0.0/0(IPv6는 ::/0)에 열려 있으면 [위험]으로 표시한다.

### 점검 전용 계정 (최소 권한)
- 루트 계정 대신 점검 전용 IAM 사용자(audit-user)를 만들어 사용
- 연결된 정책: SecurityAudit(보안 설정 조회 전용), SignInLocalDevelopmentAccess(CLI 로그인용)
- 리소스를 만들거나 지울 수 없는 읽기 전용 권한이라, 스크립트 실수가 있어도 계정에 영향이 없음
- aws login(브라우저 로그인 기반 임시 자격 증명)으로 연결해서 장기 액세스 키를 노트북에 저장하지 않음

### 실행 방법
1. pip install boto3
2. pip install "botocore[crt]"  (aws login 자격 증명을 읽기 위해 필요)
3. python scripts/check_security_groups.py

### 검증 결과
| 상황 | 결과 |
|---|---|
| 정상 구성 (default 2개, bastion-sg, web-sg) | 위험 0개 / 통과 4개 |
| SSH를 0.0.0.0/0에 연 테스트용 보안 그룹 추가 | test-open-sg를 [위험]으로 탐지 (위험 1개 / 통과 4개) |
| 테스트용 보안 그룹 삭제 후 재실행 | 위험 0개 / 통과 4개로 복귀 |

정상 설정은 통과시키고 위험한 설정은 탐지하는 것을 둘 다 확인했다.
테스트용 보안 그룹은 어떤 인스턴스에도 연결하지 않았고 확인 직후 삭제했다.

### 배운 점
- SSH를 전 세계에 여는 것이 위험한 이유: 자동 스캐너가 22번 포트를 계속 탐색하고, 공격 가능한 대상이 늘어난다
- 점검 도구는 "통과"만이 아니라 "위험을 실제로 잡아내는지"도 검증해야 신뢰할 수 있다
- 점검 전용 계정은 필요한 최소 권한(조회)만 부여한다### IAM 정책 점검 (scripts/check_iam_policies.py)
직접 만든 고객 관리형 IAM 정책을 읽어서 권한이 지나치게 넓은 정책을 찾는다.
- [위험]: Allow 문장에서 Action이 *, Resource가 * 인 정책 (모든 작업을 모든 리소스에 허용)
- [주의]: s3:* 처럼 서비스 전체 작업을 모든 리소스(*)에 허용하는 정책
- [통과]: 위 경우에 해당하지 않는 정책

실행: python scripts/check_iam_policies.py

#### 검증 결과
| 점검 대상 | 결과 |
|---|---|
| 3단계에서 만든 과다 권한 정책 (Action *, Resource *) | [위험] |
| 3단계에서 최소 권한으로 고친 정책 | [통과] |

요약: 위험 1개 / 주의 0개 / 통과 1개

#### 한계
- 고객 관리형 정책만 점검한다. 역할이나 사용자에 직접 붙인 인라인 정책과 AWS 관리형 정책(AdministratorAccess 등)은 점검하지 않는다
- Condition, NotAction 같은 복잡한 정책 문법은 해석하지 않는다### 퍼블릭 IP 인스턴스 점검 (scripts/check_public_instances.py)
실행 중인 EC2 인스턴스 중 퍼블릭 IP가 있어 인터넷에서 직접 접근할 수 있는 것을 찾는다.
퍼블릭 IP가 있는 인스턴스는 연결된 보안 그룹 이름도 함께 표시한다.

실행: python scripts/check_public_instances.py

#### 검증 결과
| 인스턴스 | 결과 |
|---|---|
| bastion-host (bastion-sg) | [공개] 퍼블릭 IP 있음 |
| web-server | [비공개] 퍼블릭 IP 없음 |

요약: 공개 1대 / 비공개 1대
설계한 대로 인터넷에 직접 노출되는 인스턴스는 bastion 한 대뿐이고, 웹서버는 프라이빗 서브넷에서 퍼블릭 IP 없이 동작한다.

#### 한계
- 실행 중(running)인 인스턴스만 점검한다
- 퍼블릭 IP가 있는 것만 확인하며, 로드밸런서나 NAT Gateway 같은 다른 공개 경로는 점검하지 않는다