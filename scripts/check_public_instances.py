import boto3

REGION = "ap-northeast-2"


def get_name(instance):
    """인스턴스의 Name 태그를 돌려준다. 없으면 (이름 없음)."""
    for tag in instance.get("Tags", []):
        if tag["Key"] == "Name":
            return tag["Value"]
    return "(이름 없음)"


def main():
    ec2 = boto3.client("ec2", region_name=REGION)

    # 실행 중인 인스턴스만 점검
    paginator = ec2.get_paginator("describe_instances")
    pages = paginator.paginate(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )

    instances = []
    for page in pages:
        for reservation in page["Reservations"]:
            instances.extend(reservation["Instances"])

    print(f"점검 리전: {REGION} / 실행 중인 인스턴스 {len(instances)}대")
    print("-" * 60)

    public_count = 0
    for inst in instances:
        name = get_name(inst)
        instance_id = inst["InstanceId"]
        public_ip = inst.get("PublicIpAddress")

        if public_ip:
            public_count += 1
            sg_names = ", ".join(sg["GroupName"] for sg in inst["SecurityGroups"])
            print(f"[공개] {name} ({instance_id})")
            print(f"       - 퍼블릭 IP가 있어 인터넷에서 직접 접근 가능")
            print(f"       - 연결된 보안 그룹: {sg_names}")
        else:
            print(f"[비공개] {name} ({instance_id}) - 퍼블릭 IP 없음")

    print("-" * 60)
    private_count = len(instances) - public_count
    print(f"결과: 공개 {public_count}대 / 비공개 {private_count}대")


if __name__ == "__main__":
    main()