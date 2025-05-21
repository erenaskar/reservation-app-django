import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

# Django ortamını ayarla
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventbooker.settings')
django.setup()

from events.models import User, Event

# Admin kullanıcısını al (ilk süper kullanıcı)
try:
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        print("Admin kullanıcı bulunamadı!")
        exit()
        
    # Etkinlik başlıkları
    event_titles = [
        "Rock Konseri: Anadolu Rüzgarı",
        "Klasik Müzik Gecesi: Chopin ve Mozart",
        "Teknoloji Zirvesi 2025",
        "Dijital Pazarlama Konferansı",
        "Yoga ve Meditasyon Atölyesi",
        "Gastronomi Festivali",
        "Modern Dans Gösterisi",
        "Fotoğrafçılık Semineri",
        "Tiyatro: Romeo ve Juliet",
        "Film Festivali 2025"
    ]
    
    # Etkinlik açıklamaları
    event_descriptions = [
        "Yerli rock gruplarının sahne alacağı muhteşem bir gece sizi bekliyor. Anadolu ezgileri ve rock müziğin muhteşem birleşimi bu gecede yer almak için acele edin.",
        "Klasik müziğin en sevilen eserlerinden oluşan bir program ile usta piyanistler tarafından Chopin ve Mozart'ın ölümsüz eserleri seslendirilecek.",
        "Yapay zeka, blok zincir ve bulut teknolojileri konusundaki son gelişmelerin konuşulacağı, sektör liderlerinin katılımıyla gerçekleşecek zirvemize davetlisiniz.",
        "Dijital pazarlamanın güncel trendleri, SEO stratejileri ve sosyal medya pazarlaması hakkında uzman konuşmacılardan bilgi alabileceğiniz konferans.",
        "Zihin ve beden sağlığınız için profesyonel eğitmenler eşliğinde yoga ve meditasyon tekniklerini öğrenebileceğiniz atölye çalışması.",
        "Yerel ve uluslararası mutfaklardan lezzetlerin sunulduğu, şef gösterileri ve yemek workshoplarının düzenleneceği gastronomi festivali.",
        "Çağdaş dans performansları, sokak dansları ve geleneksel dans türlerinin harmanlandığı özel bir gösteri gecesi.",
        "Profesyonel fotoğrafçılar eşliğinde temel ve ileri düzey fotoğrafçılık teknikleri üzerine kapsamlı bir seminer.",
        "Shakespeare'in ölümsüz eseri Romeo ve Juliet'in modern bir yorumu ile karşınızdayız. Aşkın ve dramın buluştuğu muhteşem bir gösteri.",
        "Yerli ve yabancı bağımsız filmlerin gösterildiği, yönetmenlerle söyleşilerin düzenlendiği film festivali."
    ]
    
    # Şehirler
    cities = ["İstanbul", "Ankara", "İzmir", "Antalya", "Bursa", "Adana", "Trabzon", "Konya", "Eskişehir", "Kayseri"]
    
    # Mekanlar
    locations = [
        "Açıkhava Tiyatrosu",
        "Kültür Merkezi",
        "Kongre Salonu",
        "Fuar Alanı",
        "Spor Kompleksi",
        "Sanat Galerisi",
        "Festival Parkı",
        "Üniversite Kampüsü",
        "Sahil Etkinlik Alanı",
        "Tarihi Bina"
    ]
    
    # Etkinlikleri oluştur
    created_events = 0
    current_date = timezone.now()
    
    for i in range(10):
        # Her etkinlik için benzersiz değerler
        title = event_titles[i]
        description = event_descriptions[i]
        event_date = current_date + timedelta(days=random.randint(7, 60))
        price = round(random.uniform(50, 500), 2)  # 50 ile 500 TL arası rastgele fiyat
        capacity = random.randint(50, 500)  # 50 ile 500 arası rastgele kapasite
        city = cities[i]
        location = f"{city} {locations[i]}"
        
        # Etkinliği oluştur
        event = Event.objects.create(
            title=title,
            description=description,
            event_date=event_date,
            price=price,
            capacity=capacity,
            location=location,
            city=city,
            creator=admin_user
        )
        
        created_events += 1
        print(f"Etkinlik oluşturuldu: {title}, Tarih: {event_date}, Fiyat: {price} TL, Kapasite: {capacity}")
    
    print(f"\nToplam {created_events} etkinlik başarıyla oluşturuldu.")
    
except Exception as e:
    print(f"Hata oluştu: {e}") 