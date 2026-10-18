
import boto3

REGION = "ap-northeast-2"


def as_list(value):
    """문자열 하나 또는 리스트를 항상 리스트로 바꿔준다."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def find_risky_statements(document):
    """정책 문서에서 권한이 지나치게 넓은 문장(Statement)을 찾는다."""
    findings = []
    for stmt in as_list(document.get("Statement")):
        # 허용(Allow) 문장만 점검 대상
        if stmt.get("Effect") != "Allow":
            continue

        actions = as_list(stmt.get("Action"))
        resources = as_list(stmt.get("Resource"))

        # 리소스를 특정하지 않고 모든 리소스(*)에 적용되는 경우만 문제
        if "*" not in resources:
            continue

        if "*" in actions:
            findings.append(("위험", "모든 작업(*)을 모든 리소스(*)에 허용"))
        else:
            for action in actions:
                if action.endswith(":*"):
                    findings.append(("주의", f"{action} 전체를 모든 리소스(*)에 허용"))
    return findings


def main():
    iam = boto3.client("iam", region_name=REGION)

    # 내가 직접 만든 정책(고객 관리형)만 가져온다
    policies = []
    for page in iam.get_paginator("list_policies").paginate(Scope="Local"):
        policies.extend(page["Policies"])

    print(f"점검 대상: 고객 관리형 IAM 정책 {len(policies)}개")
    print("-" * 60)

    danger_count = 0
    warn_count = 0
    for policy in policies:
        version = iam.get_policy_version(
            PolicyArn=policy["Arn"], VersionId=policy["DefaultVersionId"]
        )
        findings = find_risky_statements(version["PolicyVersion"]["Document"])

        levels = {level for level, _ in findings}
        if "위험" in levels:
            danger_count += 1
            label = "위험"
        elif "주의" in levels:
            warn_count += 1
            label = "주의"
        else:
            label = "통과"

        print(f"[{label}] {policy['PolicyName']}")
        for level, message in findings:
            print(f"       - ({level}) {message}")

    print("-" * 60)
    passed = len(policies) - danger_count - warn_count
    print(f"결과: 위험 {danger_count}개 / 주의 {warn_count}개 / 통과 {passed}개")


if __name__ == "__main__":
    main()