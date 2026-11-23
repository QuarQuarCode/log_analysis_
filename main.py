from log_analysis import analyze_logs
from alerts import check_alerts
from reports import show_report, rank_ips


def main():
    results = analyze_logs("login_logs.txt")

    failed_count, success_count, failed_by_ip, success_by_ip, failed_times_by_ip = results

    show_report(
        failed_count,
        success_count,
        failed_by_ip,
        success_by_ip
    )

    check_alerts(failed_by_ip, threshold=1  )
    rank_ips(failed_by_ip)


if __name__ == "__main__":
    main()
