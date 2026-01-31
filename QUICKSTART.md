# 🚀 QUICKSTART GUIDE - Video Downloader Pro Backend

## 1️⃣ Kurulum (1 Dakika)

```bash
# 1. Virtual environment oluştur
python -m venv venv

# 2. Aktifleştir
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Kütüphaneleri yükle
pip install -r requirements.txt
```

## 2️⃣ Sunucuyu Başlat (3 Saniye)

```bash
# Seçenek 1: Quick start (Önerilen)
python run.py

# Seçenek 2: Uvicorn
uvicorn app.main:app --reload

# Seçenek 3: Direct
python app/main.py
```

## 3️⃣ Test Et (5 Saniye)

Tarayıcında aç:
```
http://localhost:8000/docs
```

veya terminal'de:

```bash
# Health check
curl http://localhost:8000/api/health

# Video fetch (GET)
curl "http://localhost:8000/api/fetch?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Video fetch (POST)
curl -X POST "http://localhost:8000/api/fetch" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tiktok.com/@user/video/123"}'
```

## 4️⃣ Test Script

```bash
# Test scriptini çalıştır
pip install rich  # Test için gerekli
python test_api.py
```

## 🎯 Hızlı Örnekler

### Python ile kullanım

```python
import requests

# Video bilgisi al
response = requests.post(
    "http://localhost:8000/api/fetch",
    json={"url": "https://www.instagram.com/reel/ABC123/"}
)

data = response.json()
print(f"Başlık: {data['title']}")
print(f"İndirme linki: {data['direct_url']}")
print(f"Thumbnail: {data['thumbnail']}")
```

### JavaScript/Fetch ile kullanım

```javascript
fetch('http://localhost:8000/api/fetch', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://www.tiktok.com/@user/video/123'
  })
})
.then(r => r.json())
.then(data => {
  console.log('Title:', data.title);
  console.log('Download URL:', data.direct_url);
});
```

## ⚡ Önemli Endpointler

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/fetch` | POST/GET | Video bilgisi çek |
| `/api/health` | GET | Sunucu sağlık kontrolü |
| `/api/platforms` | GET | Desteklenen platformlar |
| `/docs` | GET | API dokümantasyonu |

## 🔧 Yaygın Sorunlar

### Port kullanımda
```bash
# Farklı port kullan
PORT=8080 python run.py
```

### ModuleNotFoundError
```bash
# Kütüphaneleri tekrar yükle
pip install -r requirements.txt --force-reinstall
```

### CORS hatası
```bash
# .env dosyasında frontend URL'i ekle
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

## 📝 .env Ayarları

```env
# Önemli ayarlar
DEBUG=True                    # Development modunda True
PORT=8000                     # Sunucu portu
ALLOWED_ORIGINS=...           # Frontend URL'leri (virgülle ayır)
RATE_LIMIT_PER_MINUTE=30     # Rate limit
MAX_DOWNLOAD_SIZE_MB=500     # Max dosya boyutu
```

## 🎓 Sonraki Adımlar

1. ✅ Backend çalışıyor
2. 🎨 Frontend'i kur (Next.js)
3. 🔗 Frontend'i backend'e bağla
4. 🚀 Production'a deploy et

## 💡 Pro Tips

- **Rate limit test**: 30'dan fazla istek atarsanız 429 hatası döner
- **TikTok**: Otomatik olarak watermark-free format seçilir
- **Logs**: `logs/app.log` dosyasını takip edin
- **Docs**: `/docs` endpoint'i interactive API testi için mükemmel

---

**Sorun mu var?** README.md dosyasına bak veya issue aç! 🤝
