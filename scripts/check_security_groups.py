import boto3

# 점검할 리전과 민감한 포트 목록
REGION = "ap-northeast-2"
SENSITIVE_PORTS = {
    22: "SSH",
    3389: "RDP",
    3306: "MySQL",
    5432: "PostgreSQL",
    1433: "MSSQL",
    6379: "Redis",
    27017: "MongoDB",
}
OPEN_CIDRS = ("0.0.0.0/0", "::/0")


def find_risky_rules(sg):
    """보안 그룹 하나의 인바운드 규칙 중 위험한 것을 찾아서 목록으로 돌려준다."""
    findings = []
    for rule in sg["IpPermissions"]:
        # 이 규칙이 전 세계(IPv4 또는 IPv6)에 열려 있는지 확인
        open_v4 = any(r.get("CidrIp") in OPEN_CIDRS for r in rule.get("IpRanges", []))
        open_v6 = any(r.get("CidrIpv6") in OPEN_CIDRS for r in rule.get("Ipv6Ranges", []))
        if not (open_v4 or open_v6):
            continue

        # 프로토콜이 -1이면 모든 포트가 열려 있다는 뜻
        if rule.get("IpProtocol") == "-1":
            findings.append("모든 포트가 전 세계에 열려 있음")
            continue

        from_port = rule.get("FromPort")
        to_port = rule.get("ToPort")
        if from_port is None or to_port is None:
            continue

        # 열린 포트 범위 안에 민감한 포트가 들어 있는지 확인
        for port, name in SENSITIVE_PORTS.items():
            if from_port <= port <= to_port:
                findings.append(f"{name}({port}) 포트가 전 세계에 열려 있음")
    return findings


def main():
    ec2 = boto3.client("ec2", region_name=REGION)
    groups = ec2.describe_security_groups()["SecurityGroups"]

    print(f"점검 리전: {REGION} / 보안 그룹 {len(groups)}개")
    print("-" * 60)

    risky_count = 0
    for sg in groups:
        findings = find_risky_rules(sg)
        if findings:
            risky_count += 1
            print(f"[위험] {sg['GroupName']} ({sg['GroupId']})")
            for finding in findings:
                print(f"       - {finding}")
        else:
            print(f"[통과] {sg['GroupName']} ({sg['GroupId']})")

    print("-" * 60)
    print(f"결과: 위험 {risky_count}개 / 통과 {len(groups) - risky_count}개")


if __name__ == "__main__":
    main()