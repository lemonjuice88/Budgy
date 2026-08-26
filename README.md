# Budgy

Ortak bütçe ve hedef planlama uygulaması. Birden fazla kullanıcı aynı bütçeye
katılıp ortaklaşa para ekleyebilir, farklı para birimlerinde katkı yapabilir,
tasarruflarını kaydedebilir ve hedefe ne kadar yaklaştıklarını canlı bir
grafikle takip edebilir.

**Canlı demo:** https://budgy-r3vf.onrender.com

## Özellikler

- E-posta + kullanıcı adı ile kayıt, JWT ile kimlik doğrulama
- Bütçe oluşturma, davet kodu veya bütçe ID'siyle bütçeye katılma (many-to-many)
- Bütçeye istediğin para biriminde (TRY, EUR, USD, GBP, CHF) katkı ekleme —
  anlık kur üzerinden otomatik çevrim ([Frankfurter API](https://frankfurter.dev))
- "Tasarruf Ettim" özelliği: harcamadığın parayı da bütçeye pozitif katkı olarak ekle
- Animasyonlu pasta grafikle ilerleme takibi, detaylı katkı geçmişi tablosu
- Bütçeyi tamamlama / silme; tamamlanan hedefler ayrı bir sekmede

## Teknoloji

- **Backend:** FastAPI, SQLAlchemy (async), Pydantic, JWT (PyJWT), bcrypt
- **Veritabanı:** Geliştirmede SQLite, üretimde PostgreSQL (`DATABASE_URL` değişimiyle, kod değişmeden)
- **Frontend:** Vanilla HTML/CSS/JS (build adımı yok), Chart.js ile grafik — backend tarafından aynı origin'den servis ediliyor

## Yerel kurulum

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
cp .env.example .env
.venv/Scripts/uvicorn app.main:app --reload
```

`http://localhost:8000/` adresini aç.

## Proje yapısı

```
app/
  main.py            # FastAPI app, router'ları ve statik frontend'i bağlar
  models.py          # SQLAlchemy modelleri (User, Budget, BudgetMember, Transaction)
  schemas.py         # Pydantic şemaları
  auth.py            # JWT + şifre hashleme
  database.py        # Async engine/session, DATABASE_URL normalizasyonu
  currency.py        # Anlık kur çevrimi
  budget_access.py   # Üyelik/sahiplik kontrolü (paylaşılan yardımcılar)
  routers/           # auth, budgets, transactions endpoint'leri
frontend/
  *.html, css/, js/  # Statik sayfalar (login, dashboard, bütçe detayı)
```
