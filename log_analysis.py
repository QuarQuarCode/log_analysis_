def analyze_logs(filename):
    failed_count = 0
    success_count = 0
    failed_by_ip = {}
    success_by_ip = {}
    failed_times_by_ip = {}

    with open(filename, "r") as file:
        for line in file:
            parts = line.split()

            if len(parts) < 3:
                continue

            ip = parts[0]
            time = parts[1]
            status = parts[2]

            if status == "FAILED":
                failed_count += 1
                failed_by_ip[ip] = failed_by_ip.get(ip, 0) + 1

                if ip not in failed_times_by_ip:
                    failed_times_by_ip[ip] = []

                failed_times_by_ip[ip].append(time)

            elif status == "SUCCESS":
                success_count += 1
                success_by_ip[ip] = success_by_ip.get(ip, 0) + 1

    return (
        failed_count,
        success_count,
        failed_by_ip,
        success_by_ip,
        failed_times_by_ip
    )