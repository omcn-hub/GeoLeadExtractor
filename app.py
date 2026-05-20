import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv()  # .env dosyasını yükle

# 1. Google Cloud'dan aldığın API anahtarını buraya yapıştır
API_KEY = os.getenv('API_KEY')  # .env dosyasından okunacak şekilde düzenlendi

# Aramak istediğin tüm bölgeler
bolgeler = [
    "İzmir Güzelbahçe",
    "İzmir Urla",
    "İzmir Seferihisar",
    "İzmir Çeşme"
]

# Aramak istediğin sektörlerin listesi
sektorler = [
    "Diş Klinikleri ve Poliklinikler",
    "Güzellik ve Estetik Merkezleri",
    "Mimarlık ve İç Mimarlık Ofisleri",
    "Peyzaj Ofisleri",
    "Gayrimenkul ve Emlak Danışmanlık Ofisleri",
    "Butik Oteller ve Pansiyonlar",
    "Glamping Tesisleri",
    "Özel Anaokulları ve Gündüz Bakımevleri",
    "Kolejler",
    "Özel Yaşlı Bakım Merkezleri ve Huzurevleri",
    "Havuz Yapım, İzolasyon ve Bakım Firmaları",
    "Veteriner Klinikleri",
    "Pet Otelleri",
    "Özel Tasarım Mobilya ve Kış Bahçesi"
]

sonuclar = []
url = "https://places.googleapis.com/v1/places:searchText"

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.internationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount"
}

print("🚀 Sektörel ve bölgesel veri toplama işlemi başladı...\n")

for bolge in bolgeler:
    print(f"📍 {bolge.upper()} BÖLGESİ BAŞLADI 📍")
    print("-" * 40)
    
    for sektor in sektorler:
        arama_sorgusu = f"{bolge} {sektor}"
        print(f"🔍 Aranıyor: {arama_sorgusu}...")
        
        payload = {
            "textQuery": arama_sorgusu,
            "languageCode": "tr"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                if "places" in data and len(data["places"]) > 0:
                    bulunan_sayisi = len(data["places"])
                    print(f"✔️  {bulunan_sayisi} adet işletme bulundu.")
                    
                    for place in data["places"]:
                        isletme_bilgisi = {
                            "Aranan Bölge": bolge,
                            "Hedef Sektör": sektor,
                            "İşletme Adı": place.get("displayName", {}).get("text", "-"),
                            "Adres": place.get("formattedAddress", "-"),
                            "Telefon": place.get("internationalPhoneNumber", "-"),
                            "Web Sitesi": place.get("websiteUri", "-"), # HATA DÜZELTİLDİ: websiteUri alındı
                            "Puan": place.get("rating", "-"),
                            "Yorum Sayısı": place.get("userRatingCount", "-")
                        }
                        sonuclar.append(isletme_bilgisi)
                else:
                    print(f"❌ Sonuç bulunamadı.")
            else:
                print(f"⚠️  Hata Kodu ({response.status_code}): {response.text}")
                
        except Exception as e:
            print(f"💥 Bağlantı hatası: {str(e)}")
            
        time.sleep(1)
    
    print("-" * 40)
    print(f"✔️  {bolge} bölgesi tamamlandı.\n")

if sonuclar:
    df = pd.DataFrame(sonuclar)
    df.drop_duplicates(subset=["İşletme Adı", "Adres"], keep="first", inplace=True)
    
    dosya_adi = "izmir_ege_bolgesi_isletme_listesi.xlsx"
    df.to_excel(dosya_adi, index=False)
    print(f"🎉 MUHTEŞEM! Toplam {len(df)} benzersiz işletme '{dosya_adi}' dosyasına başarıyla kaydedildi.")
else:
    print("❌ Hiç veri toplanamadı. Lütfen API anahtarınızı ve bağlantınızı kontrol edin.")