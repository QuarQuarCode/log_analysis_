
import streamlit as st
import sqlite3
from datetime import datetime
from log_analysis import analyze_logs

st.set_page_config(
    page_title="Güvenlik Takip Paneli",
    page_icon="🛡️",
    layout="wide"
)


def connect_db():
    return sqlite3.connect("security.db")


with connect_db() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            ip TEXT,
            aciklama TEXT,
            durum TEXT DEFAULT 'Açık',
            risk TEXT DEFAULT 'Orta',
            analist_notu TEXT DEFAULT ''
        )
    """)

    columns = [
        row[1] for row in
        conn.execute("PRAGMA table_info(alerts)").fetchall()
    ]

    if "risk" not in columns:
        conn.execute(
            "ALTER TABLE alerts ADD COLUMN risk TEXT DEFAULT 'Orta'"
        )

    if "analist_notu" not in columns:
        conn.execute(
            "ALTER TABLE alerts ADD COLUMN analist_notu TEXT DEFAULT ''"
        )


# GİRİŞ SİSTEMİ
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🛡️ Güvenlik Takip Sistemi")
    st.write("Güvenlik paneline erişmek için giriş yap.")

    username = st.text_input("Kullanıcı adı")
    password = st.text_input("Şifre", type="password")

    if st.button("Giriş Yap"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Kullanıcı adı veya şifre hatalı.")

    st.stop()


# MENÜ
st.sidebar.title("🛡️ Güvenlik Merkezi")

page = st.sidebar.radio(
    "Menü",
    [
        "Durum Paneli",
        "Alarmlar",
        "Karantinadaki Saldırılar"
    ]
)

if st.sidebar.button("Çıkış Yap"):
    st.session_state.logged_in = False
    st.rerun()


# LOG ANALİZİ KISMI
try:
    results = analyze_logs("login_logs.txt")

    (
        failed_count,
        success_count,
        failed_by_ip,
        success_by_ip,
        failed_times_by_ip
    ) = results

except (FileNotFoundError, ValueError):
    st.error("Log dosyası veya analiz sonuçları kontrol edilmeli.")
    st.stop()


# DURUM PANELİ
if page == "Durum Paneli":
    st.title("🛡️ Güvenlik Merkezi")
    st.caption("Güvenlik olaylarını tek noktadan takip et.")

    with connect_db() as conn:
        open_alerts = conn.execute(
            "SELECT COUNT(*) FROM alerts WHERE durum = 'Açık'"
        ).fetchone()[0]

        quarantined = conn.execute(
            "SELECT COUNT(*) FROM alerts WHERE durum = 'Karantinada'"
        ).fetchone()[0]

        ignored = conn.execute(
            "SELECT COUNT(*) FROM alerts WHERE durum = 'Yoksayıldı'"
        ).fetchone()[0]

        recent_alerts = conn.execute(
            """SELECT tarih, ip, aciklama, durum, risk
               FROM alerts ORDER BY id DESC LIMIT 10"""
        ).fetchall()

    total_attempts = failed_count + success_count
    total_ips = len(set(failed_by_ip) | set(success_by_ip))

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Genel Bakış",
        "📈 Giriş Analizi",
        "🌐 IP Analizi",
        "🚨 Son Olaylar"
    ])

    with tab1:
        st.subheader("Sistem Özeti")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Toplam Giriş", total_attempts)
        col2.metric("Başarılı Giriş", success_count)
        col3.metric("Başarısız Giriş", failed_count)
        col4.metric("Açık Alarm", open_alerts)

        st.divider()

        left, right = st.columns(2)

        with left:
            st.subheader("🔒 Tehdit Durumu")
            st.metric("Karantinadaki Kayıt", quarantined)
            st.metric("Yoksayılan Alarm", ignored)

        with right:
            st.subheader("🖥️ Sistem Özeti")
            st.metric("Takip Edilen IP", total_ips)

            if open_alerts > 0:
                st.error(f"{open_alerts} alarm inceleme bekliyor.")
            else:
                st.success("Açık alarm bulunmuyor.")

    with tab2:
        st.subheader("📈 Giriş İstatistikleri")

        col1, col2 = st.columns(2)
        col1.metric("🟢 Başarılı", success_count)
        col2.metric("🔴 Başarısız", failed_count)

        st.bar_chart({
            "Başarılı Giriş": [success_count],
            "Başarısız Giriş": [failed_count]
        })

        st.caption("Veriler login_logs.txt dosyasından alınır.")

    with tab3:
        st.subheader("🌐 Başarısız Girişler — IP Dağılımı")

        if failed_by_ip:
            sorted_ips = sorted(
                failed_by_ip.items(),
                key=lambda item: item[1],
                reverse=True
            )

            for ip, count in sorted_ips:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    col1.write(f"**IP adresi:** `{ip}`")
                    col2.metric("Başarısız Giriş", count)
        else:
            st.success("Başarısız giriş kaydı bulunmuyor.")

    with tab4:
        st.subheader("🚨 Son Güvenlik Olayları")

        if recent_alerts:
            for tarih, ip, aciklama, durum, risk in recent_alerts:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**IP:** `{ip}`")
                        st.write(aciklama)
                        st.caption(tarih)

                    with col2:
                        if risk == "Yüksek":
                            st.error("🔴 Yüksek Risk")
                        elif risk == "Orta":
                            st.warning("🟠 Orta Risk")
                        else:
                            st.success("🟢 Düşük Risk")

                        st.caption(f"Durum: {durum}")
        else:
            st.info("Henüz güvenlik alarmı bulunmuyor.")


# ALARM SAYFASI KISMI
elif page == "Alarmlar":
    st.title("🚨 Alarm Merkezi")
    st.caption("Güvenlik olaylarını incele ve yönet.")

    with st.expander("⚙️ Alarm Tarama Ayarları", expanded=True):
        threshold = st.number_input(
            "Başarısız giriş eşiği",
            min_value=1,
            value=4
        )

        if st.button("🔍 Logları Tara ve Alarm Oluştur"):
            new_alerts = 0

            with connect_db() as conn:
                for ip, count in failed_by_ip.items():
                    if count >= threshold:
                        if count >= 8:
                            risk = "Yüksek"
                        elif count >= 5:
                            risk = "Orta"
                        else:
                            risk = "Düşük"

                        existing = conn.execute(
                            """SELECT id FROM alerts
                               WHERE ip = ? AND durum = 'Açık'""",
                            (ip,)
                        ).fetchone()

                        if not existing:
                            conn.execute(
                                """INSERT INTO alerts
                                   (tarih, ip, aciklama, durum, risk)
                                   VALUES (?, ?, ?, 'Açık', ?)""",
                                (
                                    datetime.now().strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    ),
                                    ip,
                                    f"{count} başarısız giriş tespit edildi",
                                    risk
                                )
                            )
                            new_alerts += 1

            st.success(f"{new_alerts} yeni alarm oluşturuldu.")
            st.rerun()

    st.divider()

    with connect_db() as conn:
        total_alerts = conn.execute(
            "SELECT COUNT(*) FROM alerts"
        ).fetchone()[0]

        open_count = conn.execute(
            "SELECT COUNT(*) FROM alerts WHERE durum = 'Açık'"
        ).fetchone()[0]

        quarantined_count = conn.execute(
            "SELECT COUNT(*) FROM alerts WHERE durum = 'Karantinada'"
        ).fetchone()[0]

        ignored_count = conn.execute(
            "SELECT COUNT(*) FROM alerts WHERE durum = 'Yoksayıldı'"
        ).fetchone()[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📋 Toplam", total_alerts)
    col2.metric("🚨 Açık", open_count)
    col3.metric("🔒 Karantinada", quarantined_count)
    col4.metric("⚪ Yoksayıldı", ignored_count)

    st.divider()
    st.subheader("📂 Alarm Kayıtları")

    search_ip = st.text_input(
        "🔎 IP adresi ara",
        placeholder="192.168.1.10"
    )

    status_filter = st.selectbox(
        "Alarm durumu",
        ["Tümü", "Açık", "Karantinada", "Yoksayıldı"]
    )

    query = """
        SELECT id, tarih, ip, aciklama, durum, risk, analist_notu
        FROM alerts
        WHERE 1=1
    """
    params = []

    if search_ip:
        query += " AND ip LIKE ?"
        params.append(f"%{search_ip}%")

    if status_filter != "Tümü":
        query += " AND durum = ?"
        params.append(status_filter)

    query += " ORDER BY id DESC"

    with connect_db() as conn:
        rows = conn.execute(query, params).fetchall()

    st.caption(f"Gösterilen alarm sayısı: {len(rows)}")

    if rows:
        for (
            alert_id, tarih, ip, aciklama, durum, risk, analist_notu
        ) in rows:
            with st.container(border=True):
                st.subheader(f"Alarm #{alert_id}")
                st.write(f"**IP adresi:** `{ip}`")
                st.write(f"**Açıklama:** {aciklama}")
                st.caption(f"Oluşturulma tarihi: {tarih}")

                if risk == "Yüksek":
                    st.error("🔴 Risk Seviyesi: Yüksek")
                elif risk == "Orta":
                    st.warning("🟠 Risk Seviyesi: Orta")
                else:
                    st.success("🟢 Risk Seviyesi: Düşük")

                not_metni = st.text_area(
                    "Analist notu",
                    value=analist_notu or "",
                    key=f"note_{alert_id}",
                    placeholder="Örn. Test ortamından gelen trafik..."
                )

                if st.button("💾 Notu Kaydet", key=f"save_note_{alert_id}"):
                    with connect_db() as conn:
                        conn.execute(
                            """UPDATE alerts SET analist_notu = ?
                               WHERE id = ?""",
                            (not_metni, alert_id)
                        )
                    st.success("Analist notu kaydedildi.")
                    st.rerun()

                if durum == "Açık":
                    st.error("🚨 Durum: İnceleme bekliyor")
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button(
                            "🔒 Karantinaya Al",
                            key=f"quarantine_{alert_id}"
                        ):
                            with connect_db() as conn:
                                conn.execute(
                                    """UPDATE alerts SET durum = 'Karantinada'
                                       WHERE id = ? AND durum = 'Açık'""",
                                    (alert_id,)
                                )
                            st.rerun()

                    with col2:
                        if st.button(
                            "⚪ Yoksay (False Positive)",
                            key=f"ignore_{alert_id}"
                        ):
                            with connect_db() as conn:
                                conn.execute(
                                    """UPDATE alerts SET durum = 'Yoksayıldı'
                                       WHERE id = ? AND durum = 'Açık'""",
                                    (alert_id,)
                                )
                            st.rerun()

                elif durum == "Karantinada":
                    st.warning("🔒 Durum: Karantinada")
                else:
                    st.info("⚪ Durum: Yoksayıldı (False Positive)")
    else:
        st.info("Bu filtreye uygun alarm kaydı bulunamadı.")


# KARANTİNA SAYFASI KISMI
elif page == "Karantinadaki Saldırılar":
    st.title("🔒 Karantina Merkezi")
    st.caption("Karantinaya alınan güvenlik olaylarını incele ve yönet.")

    # KARANTİNA İSTATİSTİKLERİ KISMI
    with connect_db() as conn:
        total_quarantined = conn.execute(
            "SELECT COUNT(*) FROM alerts WHERE durum = 'Karantinada'"
        ).fetchone()[0]

        high_risk = conn.execute(
            """SELECT COUNT(*) FROM alerts
               WHERE durum = 'Karantinada' AND risk = 'Yüksek'"""
        ).fetchone()[0]

        unique_ips = conn.execute(
            """SELECT COUNT(DISTINCT ip) FROM alerts
               WHERE durum = 'Karantinada'"""
        ).fetchone()[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("🔒 Karantinadaki Kayıt", total_quarantined)
    col2.metric("🔴 Yüksek Risk", high_risk)
    col3.metric("🌐 Farklı IP", unique_ips)

    st.divider()

    # ARAMA VE FİLTRELER
    st.subheader("🔎 Karantina Kayıtları")

    search_ip = st.text_input(
        "IP adresi ara",
        placeholder="192.168.1.10",
        key="quarantine_search"
    )

    risk_filter = st.selectbox(
        "Risk seviyesi",
        ["Tümü", "Yüksek", "Orta", "Düşük"],
        key="quarantine_risk_filter"
    )

    query = """
        SELECT id, tarih, ip, aciklama, risk, analist_notu
        FROM alerts
        WHERE durum = 'Karantinada'
    """
    params = []

    if search_ip:
        query += " AND ip LIKE ?"
        params.append(f"%{search_ip}%")

    if risk_filter != "Tümü":
        query += " AND risk = ?"
        params.append(risk_filter)

    query += " ORDER BY id DESC"

    with connect_db() as conn:
        rows = conn.execute(query, params).fetchall()

    st.caption(f"Filtreye uyan kayıt: {len(rows)}")

    # KARANTİNA NEDENİ AÇIKLAMA
    if rows:
        for (
            alert_id, tarih, ip, aciklama, risk, analist_notu
        ) in rows:
            with st.container(border=True):
                left, right = st.columns([3, 1])

                with left:
                    st.subheader(f"Tehdit #{alert_id}")
                    st.write(f"**IP adresi:** `{ip}`")
                    st.write(f"**Tespit:** {aciklama}")
                    st.caption(f"Kayıt tarihi: {tarih}")

                    st.write(
                        "**Analist notu:**",
                        analist_notu or "Henüz not eklenmedi."
                    )

                with right:
                    if risk == "Yüksek":
                        st.error("🔴 Yüksek Risk")
                    elif risk == "Orta":
                        st.warning("🟠 Orta Risk")
                    else:
                        st.success("🟢 Düşük Risk")

                st.divider()

                if st.button(
                    "↩️ Karantinadan Çıkar ve İncelemeye Geri Al",
                    key=f"release_{alert_id}"
                ):
                    with connect_db() as conn:
                        conn.execute(
                            """UPDATE alerts
                               SET durum = 'Açık'
                               WHERE id = ? AND durum = 'Karantinada'""",
                            (alert_id,)
                        )

                    st.success(
                        f"Alarm #{alert_id} tekrar açık alarmlara taşındı."
                    )
                    st.rerun()

    else:
        st.info("Bu filtrelere uygun karantina kaydı bulunamadı.")
