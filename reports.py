def show_report(failed_count, success_count, failed_by_ip, success_by_ip):
    print("\n--- BAŞARISIZ GİRİŞLER ---")
    print("Toplam başarısız giriş:", failed_count)

    for ip, count in failed_by_ip.items():
        print(f"{ip} -> {count}")

    print("\n--- BAŞARILI GİRİŞLER ---")
    print("Toplam başarılı giriş:", success_count)

    for ip, count in success_by_ip.items():
        print(f"{ip} -> {count}")


def rank_ips(failed_by_ip):
    print("\n--- EN ÇOK BAŞARISIZ GİRİŞ YAPAN IP'LER ---")

    sorted_ips = sorted(
        failed_by_ip.items(),
        key=lambda item: item[1],
        reverse=True
    )

    for ip, count in sorted_ips:
        print(f"{ip} -> {count}")
