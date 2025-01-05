UI/UX Design and Development Guidelines

This document serves as the official UI/UX design and development guide for the application. It includes all decisions regarding the user interface, experience, and visual structure, as well as CSS best practices to ensure maintainability, scalability, and adherence to global design standards.

Design Principles
	1.	Minimal Design: Focus on functionality and readability with clean layouts and no unnecessary visual clutter.
	2.	Responsive Design: Ensure compatibility across devices (desktop, tablet, mobile).
	3.	Accessible Design: Follow WCAG 2.1 standards for accessibility (color contrast, font sizes, focus states, etc.).
	4.	Consistent Experience: Use global design tokens for colors, typography, and spacing.
	5.	Modular CSS: Avoid embedding all CSS in a single file. Components should have dedicated styles and follow BEM (Block-Element-Modifier) or utility-first naming conventions.

Theme

The application supports Light (Day) Mode and Dark (Night) Mode. Both modes are designed for maximum readability and minimal eye strain.

Light Mode
	•	Backgrounds:
	•	Main background: #F3F4F6 (Soft Light Gray)
	•	Card background: #FFFFFF (Pure White)
	•	Subtle accents: #E5E7EB (Light Gray)
	•	Text:
	•	Primary: #111827 (Dark Black)
	•	Secondary: #6B7280 (Dark Gray)
	•	Links/Actions: #2563EB (Bright Blue)

Dark Mode
	•	Backgrounds:
	•	Main background: #1F2937 (Dark Gray)
	•	Card background: #111827 (Darker Gray)
	•	Subtle accents: #374151 (Neutral Gray)
	•	Text:
	•	Primary: #F9FAFB (Off White)
	•	Secondary: #9CA3AF (Light Gray)
	•	Links/Actions: #F59E0B (Bright Orange)

Font and Typography
	1.	Font Family:
	•	San Francisco (Apple devices)
	•	Fallback: Arial, Helvetica, or system defaults.
	2.	Font Sizes:
	•	H1 (Main Titles): 32px
	•	H2-H3 (Subtitles): 24px and 18px
	•	Body Text: 16px
	•	Small Info Text: 14px
	3.	Line Height: 1.5 (150%).
	4.	Character Spacing: Standard width (for readability).

Button and Card Design
	1.	Buttons:
	•	Primary buttons: Bright colors for actions (#2563EB or #F59E0B).
	•	Hover: Slightly darker shade for visual feedback.
	•	Disabled: #E5E7EB (Neutral Gray) with a cursor disabled state.
	2.	Cards:
	•	Light mode: Pure White (#FFFFFF) background with subtle shadow (box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);).
	•	Dark mode: Darker Gray (#111827) background with faint shadow (box-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);).

Components and Layouts
	1.	Dashboard Layout:
	•	Single-column, categorized structure.
	•	Categories like Inventory, Ads, and Sales contain related visualizations.
	•	Scrolling for mobile screens with fixed category headers for easy navigation.
	2.	Chart Designs:
	•	Use Chart.js or similar libraries for:
	•	Bar Charts for stock and sales.
	•	Pie Charts for product categories.
	•	Heatmaps for seasonal sales trends.
	•	Gauge Charts for customer feedback.
	3.	Gece/Gündüz Modu Toggle:
	•	Place in the header for quick accessibility.
	•	Store preference in localStorage.

Global CSS/Utility Management
	1.	CSS Standards:
	•	Follow BEM (Block-Element-Modifier) naming convention.
	•	Use Tailwind CSS or a utility-first framework for rapid and consistent styling.
	•	Avoid inline styles unless dynamically necessary.
	2.	File Structure:
	•	/styles folder to contain:
	•	base.css: Global resets and variables.
	•	components/: Component-specific styles (e.g., button.css, card.css).
	•	utilities.css: Reusable utilities (e.g., spacing, shadows).

Additional Features for MVP
	1.	Currency Support:
	•	Use exchangeratesapi.io to fetch real-time currency conversion rates.
	•	Allow users to view metrics in USD, EUR, GBP, or local currency.
	2.	Multi-Store Support:
	•	Users can add and manage multiple Amazon stores within their account.
	•	Each store has its own dashboard and linked CSV data.
	3.	Authentication:
	•	Email/password with bcrypt for password hashing.
	•	Google OAuth for simplified login.
	•	Ensure compliance with OWASP security guidelines.

Development Notes
	1.	Scalability:
	•	Ensure every component is modular and reusable.
	•	Avoid hardcoding values; use tokens or configuration files.
	2.	Performance:
	•	Optimize assets (e.g., images, CSS, JavaScript).
	•	Lazy load charts and data-heavy components.
	3.	Testing:
	•	Ensure cross-browser and cross-device compatibility.
	•	Test both light and dark modes for accessibility.

Final Reminder
	•	The UI/UX structure and CSS setup must follow modern design standards.
	•	Do not embed all CSS into a single file. Each component and utility must have dedicated styles.
	•	Stick to the above design principles and maintain a clean, modular codebase.

# Amazon Seller Support - Tema ve UI/UX Detayları

## Veritabanı Yapısı

### Users Tablosu
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    preferred_currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Stores Tablosu
```sql
CREATE TABLE stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    store_name VARCHAR(255) NOT NULL,
    store_region VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Products Tablosu
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id INTEGER NOT NULL,
    asin VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores(id)
);
```

### Sales Tablosu
```sql
CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    sales_date DATE NOT NULL,
    sales_count INTEGER NOT NULL,
    revenue DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

### Inventory Tablosu
```sql
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    stock_level INTEGER NOT NULL,
    fulfillment_center VARCHAR(50) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

## CSV Dosya Yapıları

### 1. Business Reports
```csv
ASIN,Title,Sessions,Session Percentage,Page Views,Page Views Percentage,Buy Box Percentage,Units Ordered,Units Ordered - B2B,Unit Session Percentage,Unit Session Percentage - B2B,Ordered Product Sales,Ordered Product Sales - B2B,Total Order Items,Total Order Items - B2B
B00EXAMPLE1,Product Name 1,100,10%,150,15%,95%,10,2,10%,2%,199.90,39.98,10,2
```

### 2. Inventory Reports
```csv
ASIN,FNSKU,Product Name,Condition,Your Price,MFN Listing Exists,MFN Fulfillable Quantity,AFN Listing Exists,AFN Warehouse Quantity,AFN Fulfillable Quantity,AFN Unsellable Quantity,AFN Reserved Quantity,AFN Total Quantity,Per Unit Volume,ASIN Title
B00EXAMPLE1,X00EXAMPLE1,Product Name 1,New,19.99,Yes,0,Yes,100,95,2,3,100,0.5,Product Title 1
```

### 3. Order History
```csv
Order Date,Order ID,ASIN,Title,Category,Quantity,Price,Shipping,Tax,Total,Status,Fulfillment
2024-01-05,123-1234567-1234567,B00EXAMPLE1,Product Name 1,Electronics,1,19.99,0,1.60,21.59,Delivered,Amazon
```

## Dashboard Layout

### Kategori Bazlı Düzen

1. **Stok Analizi**
   - Stok Durumu (Bar Chart)
   - Depo Bazlı Analiz (Stacked Bar)

2. **Satış Metrikleri**
   - Satış Trendi (Line Chart)
   - Satış Performansı (Area Chart)
   - Sezonsal Analiz (Heat Map)

3. **Reklam Performansı**
   - ACOS Analizi (Line/Bar Combo)
   - ROI Metrikleri (Gauge Chart)

4. **Müşteri İçgörüleri**
   - Müşteri Yorumları (Gauge + Mini Line)
   - İade Oranları (Donut Chart)

5. **Rekabet Analizi**
   - Fiyat Karşılaştırma (Radar Chart)
   - Buy Box Oranları (Line Chart)

### Tasarım Detayları

1. **Renk Paleti**
   ```css
   :root {
     --primary: #2563eb;     /* Mavi */
     --secondary: #475569;   /* Gri */
     --success: #22c55e;     /* Yeşil */
     --warning: #eab308;     /* Sarı */
     --danger: #ef4444;      /* Kırmızı */
     --info: #3b82f6;       /* Açık Mavi */
     --light: #f8fafc;      /* Beyaz */
     --dark: #1e293b;       /* Koyu */
   }
   ```

2. **Tipografi**
   ```css
   /* Inter font ailesi */
   body {
     font-family: 'Inter', sans-serif;
   }
   
   /* Başlık hiyerarşisi */
   h1 { font-size: 2.25rem; font-weight: 700; }
   h2 { font-size: 1.875rem; font-weight: 600; }
   h3 { font-size: 1.5rem; font-weight: 600; }
   h4 { font-size: 1.25rem; font-weight: 500; }
   ```

3. **Responsive Breakpoints**
   ```css
   /* Tailwind CSS breakpoints */
   sm: '640px'   /* Mobil */
   md: '768px'   /* Tablet */
   lg: '1024px'  /* Laptop */
   xl: '1280px'  /* Desktop */
   2xl: '1536px' /* Geniş Ekran */
   ```

## Geliştirme Öncelikleri

### Faz 1: Temel Altyapı
1. Authentication sistemi
2. CSV upload ve parsing
3. Temel dashboard yapısı
4. İlk 4 grafik implementasyonu

### Faz 2: Gelişmiş Özellikler
1. Kalan grafiklerin implementasyonu
2. Para birimi desteği
3. Çoklu mağaza desteği
4. Shipment planlama

### Faz 3: Optimizasyon
1. Cache sistemi
2. Performance iyileştirmeleri
3. UI/UX geliştirmeleri
4. Test ve hata düzeltmeleri