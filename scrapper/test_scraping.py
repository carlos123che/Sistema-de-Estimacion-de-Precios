from bs4 import BeautifulSoup

html = """<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"><a class="group block bg-white rounded-2xl border border-slate-100 overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5" href="/propiedades/CVC6956"><div class="relative aspect-[4/3] overflow-hidden bg-slate-100"><img alt="NUEVO PRECIO Vendo Hermosa Mansión en Condominio Exclusivo Sausalito, Carretera a El Salvador" fetchpriority="high" loading="eager" decoding="async" data-nimg="fill" class="object-cover group-hover:scale-105 transition-transform duration-500" src="https://images.digital-guatemala.com/legacy/img/propertiesphotos/2024-11-03-1481323445.jpg" style="position: absolute; height: 100%; width: 100%; inset: 0px; color: transparent;"><div class="absolute bottom-3 left-3 px-2 py-1 rounded-full bg-red-500/90 text-white text-xs font-semibold flex items-center gap-1"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-trending-down w-3 h-3" aria-hidden="true"><path d="M16 17h6v-6"></path><path d="m22 17-8.5-8.5-5 5L2 7"></path></svg>Precio reducido</div></div><div class="p-4"><p class="text-xs font-semibold uppercase tracking-wider text-brand-700 mb-1.5">Casa en Venta</p><h3 class="text-base font-semibold text-slate-900 group-hover:text-brand-600 transition-colors line-clamp-1 mb-1">NUEVO PRECIO Vendo Hermosa Mansión en Condominio Exclusivo Sausalito, Carretera a El Salvador</h3><p class="flex items-center gap-1 text-sm text-slate-500 mb-2"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-map-pin w-3.5 h-3.5 shrink-0" aria-hidden="true"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"></path><circle cx="12" cy="10" r="3"></circle></svg><span class="truncate">Sausalito, Carretera a El Salvador, Guatemala, Ciudad</span></p><div class="flex items-baseline gap-2 mb-3"><span class="text-xl font-black text-slate-900">$1,950,000</span><span class="text-sm text-slate-400 line-through">$2,500,000</span></div><div class="flex items-center gap-4 text-sm text-slate-600"><span class="flex items-center gap-1"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bed-double w-4 h-4 text-slate-400" aria-hidden="true"><path d="M2 20v-8a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v8"></path><path d="M4 10V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v4"></path><path d="M12 4v6"></path><path d="M2 18h20"></path></svg>5</span><span class="flex items-center gap-1"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bath w-4 h-4 text-slate-400" aria-hidden="true"><path d="M10 4 8 6"></path><path d="M17 19v2"></path><path d="M2 12h20"></path><path d="M7 19v2"></path><path d="M9 5 7.621 3.621A2.121 2.121 0 0 0 4 5v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-5"></path></svg>7</span><span class="flex items-center gap-1"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-car w-4 h-4 text-slate-400" aria-hidden="true"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"></path><circle cx="7" cy="17" r="2"></circle><path d="M9 17h6"></path><circle cx="17" cy="17" r="2"></circle></svg>7</span><span class="flex items-center gap-1"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-maximize w-4 h-4 text-slate-400" aria-hidden="true"><path d="M8 3H5a2 2 0 0 0-2 2v3"></path><path d="M21 8V5a2 2 0 0 0-2-2h-3"></path><path d="M3 16v3a2 2 0 0 0 2 2h3"></path><path d="M16 21h3a2 2 0 0 0 2-2v-3"></path></svg>1400m²</span></div></div></a></div>"""

soup = BeautifulSoup(html, 'html.parser')
tarjetas = soup.select('.grid > a.group')

for tarjeta in tarjetas:
    href = tarjeta.get('href')
    titulo = tarjeta.find('h3').text.strip() if tarjeta.find('h3') else 'N/A'
    ubicacion_tag = tarjeta.find('span', class_='truncate')
    ubicacion = ubicacion_tag.text.strip() if ubicacion_tag else 'N/A'
    
    precio_tag = tarjeta.find('span', class_='text-xl font-black')
    precio = precio_tag.text.strip() if precio_tag else 'N/A'
    
    habs, banos, parqueos, area = 'N/A', 'N/A', 'N/A', 'N/A'
    
    features_div = tarjeta.find('div', class_='flex items-center gap-4')
    if features_div:
        spans = features_div.find_all('span', class_='flex items-center gap-1')
        for span in spans:
            svg = span.find('svg')
            if svg:
                classes = svg.get('class', [])
                val = span.text.strip()
                if 'lucide-bed-double' in classes:
                    habs = val
                elif 'lucide-bath' in classes:
                    banos = val
                elif 'lucide-car' in classes:
                    parqueos = val
                elif 'lucide-maximize' in classes:
                    area = val
                    
    print(f'Link: {href}')
    print(f'Titulo: {titulo}')
    print(f'Ubicacion: {ubicacion}')
    print(f'Precio: {precio}')
    print(f'Habs: {habs}, Baños: {banos}, Parqueos: {parqueos}, Area: {area}')
