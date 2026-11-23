from datetime import datetime

def check_alerts(failed_by_ip, threshold=4):
    print("Güvenlik Alarmları")

    alert_found = False
    for ip, count in failed_by_ip.items():
        if count >= threshold:
            timestamp= datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            message=(
                f"[{timestamp}]  [ALARM] {ip} adresinden"
                f" {count} başarısız giriş tespit edildi!"
            )

            print(message)

            with open("security_alerts.txt", "a", encoding="utf-8") as file:
                file.write(message + "\n")
                alert_found = True


    if not alert_found:
        print("Herhangi bir alarm bulunamadı.")

